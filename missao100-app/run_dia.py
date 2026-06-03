#!/usr/bin/env python3
"""
Missão 100% — rotina diária do Instagram no SERVIDOR.
Gera o episódio do dia (Claude API), renderiza os 10 slides, monta a legenda
e publica o carrossel no @aprendanefro (GitHub + Graph API).

Uso:
  python3 run_dia.py        -> episódio de hoje (America/Sao_Paulo)
  python3 run_dia.py 30     -> episódio 30 (teste)
"""
import sys, json, pathlib
BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE / "lib"))
import engine, slides, caption, publicar_instagram

def main(arg=None):
    cfg = engine.load_config()
    ep = engine.episodio_de(arg)            # sai vazio/erro fora da janela 1..100
    out = BASE / "saida" / f"dia-{ep['episodio']:03d}"; out.mkdir(parents=True, exist_ok=True)
    if (out / ".published.json").exists():
        print("já publicado, nada a fazer:", ep["episodio"]); return
    data = engine.gerar(ep, cfg)
    json.dump(data, open(out / "conteudo.json", "w"), ensure_ascii=False, indent=1)
    slides.render(ep["episodio"])
    (out / "legenda.txt").write_text(caption.build(data.get("legenda_instagram", ""), ep["faltam"]))
    r = publicar_instagram.publicar(ep["episodio"])
    print("publicado ep", ep["episodio"], "->", r)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
