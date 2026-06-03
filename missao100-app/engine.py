#!/usr/bin/env python3
"""
Motor de conteúdo do Missão 100% Aprovação.
Lê o episódio do dia (calendario.json) e gera, via Claude API, o pacote completo:
questão (7h), comentário/gabarito (16h) e o roteiro do carrossel de 10 slides.
Salva em saida/dia-NNN/conteudo.json.

Uso:
  python engine.py            -> gera o episódio de hoje (America/Sao_Paulo)
  python engine.py 42         -> gera o episódio 42
  python engine.py 2026-07-01 -> gera o episódio daquela data
"""
import os, sys, json, re, datetime, pathlib, urllib.request

BASE = pathlib.Path(__file__).parent
def load_config():
    cfg = json.load(open(BASE / "config.json")) if (BASE / "config.json").exists() else {}
    # variáveis de ambiente têm prioridade
    for k in ["CLAUDE_API_KEY", "CLAUDE_MODEL"]:
        if os.environ.get(k): cfg[k] = os.environ[k]
    cfg.setdefault("CLAUDE_MODEL", "claude-sonnet-4-6")
    return cfg

CAL = json.load(open(BASE / "calendario.json", encoding="utf-8"))
INICIO = datetime.date(2026, 6, 7)

def episodio_de(arg=None):
    if arg is None:
        d = datetime.date.today()
        ep = (d - INICIO).days + 1
    elif re.match(r"^\d{4}-\d{2}-\d{2}$", str(arg)):
        d = datetime.date.fromisoformat(arg); ep = (d - INICIO).days + 1
    else:
        ep = int(arg)
    for e in CAL:
        if e["episodio"] == ep: return e
    raise SystemExit(f"Sem episódio para {arg} (ep={ep}). Janela: 1..100.")

# ---------------------------------------------------------------- prompt
SYSTEM = """Você é o examinador-chefe do Missão 100% Aprovação, projeto gratuito do AprendaNefro (Dr. Marcelo Albuquerque) que prepara médicos para a PROVA DE TÍTULO DE ESPECIALISTA EM NEFROLOGIA da SBN. Público: nefrologistas e residentes avançados. Voz AprendaNefro: horizontal, próxima ("de nefrologista para nefrologista"), motivacional com lastro técnico, frases curtas, simples e rigorosa. SEM emojis decorativos em excesso, SEM hashtags, SEM tom de coach vazio, SEM vender nada.

REGRAS INVIOLÁVEIS DAS QUESTÕES:
1. DIFICULDADE MÁXIMA — nível prova de título, reflexiva, exige raciocínio clínico, não decoreba.
2. INTEGRAÇÃO DENTRO DO TEMA — a questão amarra o assunto CENTRAL com os ASSUNTOS INTEGRADOS recebidos, que são SUBTEMAS DA MESMA ÁREA (assuntos que conversam entre si). Aprofunde e cruze DENTRO do tema. NUNCA misture áreas distantes (ex.: não juntar distúrbio eletrolítico com glomerulopatia ou transplante). Ex. correto: potássio + sódio + alcalose num mesmo caso.
3. BASE EM EVIDÊNCIA — ancore em diretrizes/ensaios reais (KDIGO 2024/2025, diretrizes brasileiras SBN, PCDT, ensaios landmark). NUNCA invente números, estudos ou referências. Conservador e clinicamente correto.
4. FORMATO conforme o tipo:
   - "objetiva": vinheta clínica longa + EXATAMENTE 4 alternativas (A, B, C, D), apenas 1 correta, distratores plausíveis. Informe o gabarito e por que cada distrator está errado.
   - "subjetiva": caso clínico + EXATAMENTE 4 perguntas abertas para o aluno responder (raciocinar/escrever). Para o comentário, dê a resposta/tópicos de CADA uma das 4 perguntas.
5. COMENTÁRIO (16h) — organizado e completo (didático, mas objetivo). Use formatação de WhatsApp: *negrito* nos títulos e rótulos.
   - Subjetiva: abra com "*Visão geral do caso:*" (1–2 linhas costurando os achados). Depois responda CADA uma das 4 perguntas em bloco separado, com cabeçalho em negrito ("*1) ...*", "*2) ...*", "*3) ...*", "*4) ...*"). Em cada bloco entregue: a resposta direta, o mecanismo/porquê e os números/condutas/doses relevantes. Seja completo.
   - Objetiva: "*Gabarito: X*" + por que a correta está certa + por que CADA distrator (A, B, C, D) está errado, com a referência.
   - Termine sempre com "*Leve pra casa:*" (1–2 linhas).
6. CARROSSEL — REVISÃO PROFUNDA DE UM ÚNICO ASSUNTO, NÍVEL ESPECIALISTA: os 10 slides são uma aula densa e encadeada sobre o ASSUNTO DO DIA (o tema central), TODOS sobre o MESMO assunto — NÃO 10 assuntos diferentes. O público é nefrologista/residente avançado fazendo a prova de título: PEGUE PESADO no conteúdo, profundidade de especialista. NADA de frase superficial, óbvia ou motivacional vazia. Inclua o que diferencia: valores e alvos numéricos, doses, critérios diagnósticos, classificações, nomes de ensaios e diretrizes (KDIGO, BJN, PCDT), mecanismos, diagnósticos diferenciais finos e pegadinhas de prova. Cubra, ao longo dos 10 slides: conceito/fisiopatologia, causas/classificação, diagnóstico (clínica + laboratório + ECG/imagem), conduta e drogas (com doses/limiares), situações especiais e armadilhas, e "leve pra casa". Slide 1 = capa (título do assunto). Slides 2–9 = conteúdo DENSO que PREENCHE o slide. Slide 10 = síntese/"leve pra casa". Escrita objetiva e afiada; poupe palavras, ganhe densidade. Sem hashtags, sem encher linguiça.
FORMATO DO 'corpo' (para a diagramação): escreva de 4 a 7 PONTOS, UM POR LINHA (separe com \\n). Cada ponto é denso (pode ocupar 2–3 linhas quando quebrar na arte). Quando fizer sentido, comece o ponto com um RÓTULO CURTO seguido de ':' (ex.: "Redistribuição:", "Perda renal:", "ECG:", "Conduta:", "Doses:") — esse rótulo ganha destaque dourado no slide. Não use marcadores manuais (sem "-", "•", "1)"); só o rótulo + dois-pontos e o texto.

RESPONDA APENAS COM JSON VÁLIDO, nada fora dele, neste schema:
{
 "tema_dia": "string curta com os assuntos do dia",
 "questao_7h": "texto pronto da questão para o WhatsApp (enunciado completo; se objetiva, inclua as alternativas A-D; se subjetiva, inclua as 4 perguntas numeradas). NÃO inclua o gabarito aqui.",
 "gabarito": "objetiva: a letra correta. subjetiva: vazio.",
 "comentario_16h": "texto pronto do comentário para o WhatsApp (objetiva: alternativa correta + por que cada uma; subjetiva: resposta de cada uma das 4 perguntas; sempre com 'leve pra casa').",
 "referencias": ["lista curta de referências reais usadas"],
 "carrossel": [{"slide":1,"titulo":"...","corpo":"..."}, ... 10 slides ...],
 "legenda_instagram": "GANCHO educativo curto (2 a 4 frases) sobre o assunto do dia, na voz AprendaNefro, que provoque o estudo e resuma a ideia central. NÃO inclua chamada para ação, link nem hashtags — o bloco de CTA/captação é acrescentado automaticamente pelo sistema."
}"""

def build_user(ep):
    integ = "; ".join(ep["integrados"])
    return f"""Gere o episódio {ep['episodio']} do Missão 100% Aprovação.

TIPO: {ep['tipo']}  (objetiva = múltipla escolha 4 alt/1 correta; subjetiva = caso com 4 perguntas abertas)
DIFICULDADE: máxima
ASSUNTO CENTRAL: {ep['central']}
ASSUNTOS INTEGRADOS (amarre todos na mesma questão): {integ}
ÂNCORA (diretriz/ensaio para basear): {ep['ancora']}
CONTAGEM REGRESSIVA: faltam {ep['faltam']} dias para a prova (15/09/2026).

No começo da questao_7h, inclua um cabeçalho curto:
"MISSÃO 100% APROVAÇÃO — Episódio {ep['episodio']}/100  |  Faltam {ep['faltam']} dias para a prova"
Depois a questão. Lembre: integrar DENTRO do tema (central + integrados são subtemas da MESMA área) num único caso difícil e coerente — não misture áreas distantes. O CARROSSEL revisa SÓ o assunto central ({ep['central']}) a fundo, em 10 slides encadeados."""

def gerar(ep, cfg):
    body = {
        "model": cfg["CLAUDE_MODEL"],
        "max_tokens": 3500,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": build_user(ep)}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={"x-api-key": cfg["CLAUDE_API_KEY"], "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)
    raw = resp["content"][0]["text"].strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.I).strip()
    data = json.loads(raw)
    data["_meta"] = {"episodio": ep["episodio"], "data": ep["data"], "tipo": ep["tipo"], "faltam": ep["faltam"]}
    return data

def main():
    cfg = load_config()
    if not cfg.get("CLAUDE_API_KEY"):
        raise SystemExit("Falta CLAUDE_API_KEY (config.json ou variável de ambiente).")
    ep = episodio_de(sys.argv[1] if len(sys.argv) > 1 else None)
    data = gerar(ep, cfg)
    out = BASE / "saida" / f"dia-{ep['episodio']:03d}"
    out.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(out / "conteudo.json", "w"), ensure_ascii=False, indent=1)
    print(f"OK episódio {ep['episodio']} ({ep['tipo']}) -> {out/'conteudo.json'}")

if __name__ == "__main__":
    main()
