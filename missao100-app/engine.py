#!/usr/bin/env python3
"""
Motor do CARROSSEL do Missão 100% (Instagram). Lê o episódio do dia (calendario.json)
e gera, via Claude API, APENAS o carrossel de 10 slides + a legenda (a questão/comentário
do WhatsApp são gerados pelo n8n, à parte). Salva em saida/dia-NNN/conteudo.json.
"""
import os, sys, json, re, datetime, pathlib, urllib.request

BASE = pathlib.Path(__file__).parent
def load_config():
    cfg = json.load(open(BASE / "config.json")) if (BASE / "config.json").exists() else {}
    for p in [BASE / ".credenciais.json"]:
        if p.exists(): cfg = {**json.load(open(p)), **cfg}
    for k in ["CLAUDE_API_KEY", "CLAUDE_MODEL"]:
        if os.environ.get(k): cfg[k] = os.environ[k]
    cfg.setdefault("CLAUDE_MODEL", "claude-sonnet-4-6")
    return cfg

CAL = json.load(open(BASE / "calendario.json", encoding="utf-8"))
INICIO = datetime.date(2026, 6, 7)

def episodio_de(arg=None):
    if arg is None:
        ep = (datetime.date.today() - INICIO).days + 1
    elif re.match(r"^\d{4}-\d{2}-\d{2}$", str(arg)):
        ep = (datetime.date.fromisoformat(arg) - INICIO).days + 1
    else:
        ep = int(arg)
    for e in CAL:
        if e["episodio"] == ep: return e
    raise SystemExit(f"Sem episódio para {arg} (ep={ep}). Janela: 1..100.")

SYSTEM = """Você é o professor do Missão 100% Aprovação (AprendaNefro), criando o CARROSSEL DIÁRIO do Instagram para preparar médicos para a prova de título de nefrologia da SBN. Público: nefrologistas e residentes avançados. Voz horizontal, motivacional com lastro técnico. Pode usar emojis com moderação. Sem hashtags. Não venda nada.

O carrossel é uma REVISÃO PROFUNDA, NÍVEL ESPECIALISTA, de UM ÚNICO ASSUNTO (o tema central do dia) — 10 slides encadeados, TODOS sobre o MESMO assunto. PEGUE PESADO no conteúdo: valores e alvos numéricos, doses, critérios diagnósticos, classificações, nomes de ensaios e diretrizes (KDIGO, SBN, PCDT), mecanismos, diagnósticos diferenciais finos e pegadinhas de prova. NADA superficial, óbvio ou motivacional vazio. Baseado em evidência real; NUNCA invente números nem estudos.

Estrutura dos 10 slides (cobrindo o tema a fundo, nesta ordem): slide 1 = capa (apenas o título do assunto, corpo vazio); slides 2–9 = conteúdo DENSO que preenche o slide; slide 10 = síntese / "leve pra casa". Ao longo deles cubra: conceito/fisiopatologia, causas/classificação, diagnóstico (clínica + laboratório + ECG/imagem), conduta e drogas (com doses/limiares), situações especiais e armadilhas.

FORMATO DO 'corpo' de cada slide (para a diagramação): de 4 a 7 PONTOS, UM POR LINHA (separe com \\n). Cada ponto denso e objetivo. Quando fizer sentido, comece o ponto com um RÓTULO CURTO seguido de ':' (ex.: "Causas:", "ECG:", "Conduta:", "Doses:", "Armadilha:"). NÃO use marcadores manuais (sem "-", "•", "1)").

A legenda do Instagram: um gancho educativo curto (2 a 4 frases) sobre o assunto, na voz AprendaNefro, SEM chamada para ação e SEM hashtags.

RESPONDA APENAS COM JSON VÁLIDO, nada fora dele. Use \\n para quebras de linha dentro das strings (NÃO use quebras de linha reais dentro do JSON). Schema exato:
{"tema_dia":"...","carrossel":[{"slide":1,"titulo":"...","corpo":"..."}, ... 10 slides ...],"legenda_instagram":"..."}"""

def build_user(ep):
    integ = ", ".join(ep["integrados"])
    return (f"Gere o carrossel do episódio {ep['episodio']}/100 do Missão 100%. "
            f"ASSUNTO CENTRAL (revise SÓ ele, a fundo, nos 10 slides): {ep['central']}. "
            f"Faltam {ep['faltam']} dias para a prova. "
            f"Subtemas relacionados (da mesma área) que podem aparecer: {integ}. "
            f"Âncora/base: {ep['ancora']}.")

def gerar(ep, cfg):
    if not cfg.get("CLAUDE_API_KEY"):
        raise SystemExit("Falta CLAUDE_API_KEY (config.json).")
    body = {"model": cfg["CLAUDE_MODEL"], "max_tokens": 6000, "system": SYSTEM,
            "messages": [{"role": "user", "content": build_user(ep)}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={"x-api-key": cfg["CLAUDE_API_KEY"], "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.load(r)
    raw = resp["content"][0]["text"].strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
    raw = re.sub(r"\s*```$", "", raw).strip()
    a, b = raw.find("{"), raw.rfind("}")
    if a >= 0 and b > a: raw = raw[a:b+1]
    data = json.loads(raw)
    data["_meta"] = {"episodio": ep["episodio"], "data": ep["data"], "tipo": ep["tipo"], "faltam": ep["faltam"]}
    return data

if __name__ == "__main__":
    cfg = load_config()
    ep = episodio_de(sys.argv[1] if len(sys.argv) > 1 else None)
    data = gerar(ep, cfg)
    out = BASE / "saida" / f"dia-{ep['episodio']:03d}"; out.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(out / "conteudo.json", "w"), ensure_ascii=False, indent=1)
    print(f"OK episódio {ep['episodio']} -> {out/'conteudo.json'}")
