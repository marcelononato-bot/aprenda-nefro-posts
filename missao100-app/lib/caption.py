"""
Monta a legenda do post do Instagram:
  [gancho educativo do dia, gerado pelo motor]
  + [bloco fixo: identidade do projeto + contagem regressiva + CTA do ManyChat]

O CTA é FIXO de propósito: a automação do ManyChat dispara quando o aluno
comenta a palavra-chave (PROVA) e envia o link do grupo de WhatsApp no direct.
Instagram não renderiza *negrito* — manter texto puro, sem hashtags.
"""

PALAVRA_CHAVE = "PROVA"

CTA = (
    "—\n"
    "Missão 100% Aprovação: revisão diária e gratuita para a Prova de Título de "
    "Especialista em Nefrologia (SBN). Contagem regressiva: faltam {faltam} dias.\n\n"
    "Quer receber a questão de todo dia? Comente {kw} aqui embaixo que a gente te "
    "envia no direct o link do grupo de WhatsApp do projeto — uma questão por dia no "
    "nível da prova, com o comentário saindo no fim da tarde.\n\n"
    "Aberto a todo mundo que vai encarar a prova de título, residentes inclusive. "
    "Uma jornada AprendaNefro."
)

def build(gancho, faltam):
    gancho = (gancho or "").strip()
    bloco = CTA.format(faltam=faltam, kw=PALAVRA_CHAVE)
    return f"{gancho}\n\n{bloco}" if gancho else bloco
