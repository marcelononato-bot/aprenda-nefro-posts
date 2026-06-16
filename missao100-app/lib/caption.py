"""
Monta a legenda do post do Instagram.

A legenda é APENAS a chamada (CTA) para o grupo de WhatsApp: a automação do
ManyChat dispara quando a pessoa comenta a palavra-chave (PROVA) e envia o link
do grupo no direct. Sem gancho educativo, sem hashtags. Instagram não renderiza
*negrito*, então o texto é puro.
"""

PALAVRA_CHAVE = "PROVA"

CTA = (
    "Vai fazer a Prova de Título de Especialista em Nefrologia da SBN? "
    "Então esse grupo é pra você.\n\n"
    "A Missão 100% Aprovação é uma preparação diária e gratuita: todo dia uma "
    "questão no nível da prova e, no fim da tarde, o comentário completo. "
    "Faltam {faltam} dias.\n\n"
    "👉 Comente {kw} aqui embaixo que a gente te manda no direct o link do "
    "grupo de WhatsApp do projeto.\n\n"
    "Especialistas e residentes que vão encarar a prova, todos são bem-vindos. "
    "Uma jornada AprendaNefro."
)

def build(gancho, faltam):
    # 'gancho' é ignorado de propósito: a legenda é só o CTA do grupo.
    return CTA.format(faltam=faltam, kw=PALAVRA_CHAVE)
