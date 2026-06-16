"""
Publicador do Missão 100% para o SERVIDOR (espelha o /opt/ccn):
sobe os 10 slides do dia para o repo GitHub `aprenda-nefro-posts` (GitHub Contents API)
e publica o carrossel no @aprendanefro via Instagram Graph API.

Reaproveita as MESMAS credenciais do Café com Nefro (.credenciais.json):
PAGE_ACCESS_TOKEN, IG_BUSINESS_ID, GH_TOKEN — só acrescenta GH_OWNER/GH_REPO/GH_BRANCH
(que já são constantes no publicar do CCN).
"""
import os, json, time, base64, pathlib, urllib.request, urllib.error, urllib.parse

BASE = pathlib.Path(__file__).parents[1]
GV = "v21.0"

def _cfg():
    # tenta config.json do projeto; se faltar, cai pro .credenciais.json (mesmo do CCN)
    cfg = {}
    for p in [BASE / "config.json", BASE / ".credenciais.json"]:
        if p.exists():
            cfg.update(json.load(open(p)))
    cfg.setdefault("GH_REPO", "aprenda-nefro-posts")
    cfg.setdefault("GH_BRANCH", "main")
    cfg.setdefault("IG_SUBFOLDER", "missao100")
    return cfg

def _gh_put(cfg, repo_path, data_bytes, msg):
    owner, repo, branch = cfg["GH_OWNER"], cfg["GH_REPO"], cfg["GH_BRANCH"]
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_path}"
    headers = {"Authorization": f"Bearer {cfg['GH_TOKEN']}",
               "Accept": "application/vnd.github+json", "User-Agent": "missao100"}
    body = {"message": msg, "content": base64.b64encode(data_bytes).decode(), "branch": branch}
    # se já existir, precisa do sha
    try:
        g = urllib.request.Request(api + f"?ref={branch}", headers=headers)
        with urllib.request.urlopen(g, timeout=30) as r:
            body["sha"] = json.load(r)["sha"]
    except urllib.error.HTTPError:
        pass
    req = urllib.request.Request(api, data=json.dumps(body).encode(), headers=headers, method="PUT")
    with urllib.request.urlopen(req, timeout=60) as r:
        json.load(r)
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{repo_path}"

def _api(path, params, method="POST"):
    url = f"https://graph.facebook.com/{GV}/{path}"
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        url += "?" + data.decode(); data = None
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # inclui a mensagem do Graph no erro (pra aparecer no log)
        body = e.read().decode("utf-8", "ignore")[:400]
        raise urllib.error.HTTPError(e.url, e.code, f"{e.reason} :: {body}", e.headers, None)

def _child(ig, tok, u):
    # cria o container-filho com RETRIES: o raw do GitHub pode demorar a propagar
    # e o Facebook devolve 400 ao tentar buscar a imagem cedo demais.
    last = None
    for wait in (0, 10, 20, 40, 60):
        if wait:
            time.sleep(wait)
        try:
            return _api(f"{ig}/media", {"image_url": u, "is_carousel_item": "true", "access_token": tok})["id"]
        except urllib.error.HTTPError as e:
            last = e
            print(f"  retry container (img ainda nao propagou?): {e}")
    raise last

def publicar(ep_num):
    cfg = _cfg()
    out = BASE / "saida" / f"dia-{ep_num:03d}"
    data = json.load(open(out / "conteudo.json"))
    legenda = (out / "legenda.txt").read_text() if (out / "legenda.txt").exists() else data.get("legenda_instagram", "")
    ig, tok = cfg["IG_BUSINESS_ID"], cfg["PAGE_ACCESS_TOKEN"]
    # 1) sobe os 10 slides pro GitHub e coleta as URLs
    urls = []
    for i in range(1, 11):
        f = out / f"slide-{i:02d}.png"
        repo_path = f"{cfg['IG_SUBFOLDER']}/dia-{ep_num:03d}/slide-{i:02d}.png"
        urls.append(_gh_put(cfg, repo_path, f.read_bytes(), f"missao100 dia {ep_num} slide {i}"))
    time.sleep(8)  # folga inicial para o raw do GitHub propagar
    # 2) cria os containers-filhos (com retry: tolera atraso de propagação do raw)
    children = [_child(ig, tok, u) for u in urls]
    # 3) container do carrossel
    car = _api(f"{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(children),
                               "caption": legenda, "access_token": tok})
    for _ in range(20):
        st = _api(f"{car['id']}", {"fields": "status_code", "access_token": tok}, "GET")
        if st.get("status_code") == "FINISHED": break
        time.sleep(5)
    pub = _api(f"{ig}/media_publish", {"creation_id": car["id"], "access_token": tok})
    json.dump({"published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "media_id": pub.get("id"), "method": "vps_cron"},
              open(out / ".published.json", "w"))
    return pub

if __name__ == "__main__":
    import sys
    print(publicar(int(sys.argv[1])))
