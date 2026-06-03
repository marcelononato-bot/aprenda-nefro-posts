# Deploy do Instagram no servidor (DigitalOcean) — Missão 100%

Espelha o `/opt/ccn` (Café com Nefro). Roda 24/7, computador desligado. Publica às 16h.
Reaproveita as MESMAS credenciais e o MESMO repo GitHub (`aprenda-nefro-posts`) — mesma conta @aprendanefro.

## O que esta rotina faz (todo dia 16h)
`run_dia.py`: pega o episódio do dia (calendário) → gera o conteúdo (Claude API) → renderiza os 10 slides → sobe as imagens no GitHub → publica o carrossel via Graph API. Fora da janela 07/jun–14/set, não faz nada.

## Passo 1 — Colocar o código em /opt/missao100
Pelo Console do droplet (terminal), com o pacote já num repositório GitHub:
```
git clone https://github.com/SEU-USUARIO/missao100-app.git /opt/missao100
cd /opt/missao100
```
(Vamos preparar esse repositório juntos — é só arrastar os arquivos no GitHub.)

## Passo 2 — Ambiente Python (venv) + Pillow
```
cd /opt/missao100
python3 -m venv venv
./venv/bin/pip install --upgrade pip pillow
mkdir -p logs saida
```

## Passo 3 — Credenciais (reaproveitando o Café com Nefro)
```
# copia o .credenciais.json que já funciona (PAGE_ACCESS_TOKEN, IG_BUSINESS_ID, GH_TOKEN)
cp /opt/ccn/.credenciais.json /opt/missao100/.credenciais.json
# descobre o seu usuário do GitHub usado no CCN
grep -i GH_OWNER /opt/ccn/publicar_instagram.py
```
Crie o `config.json` com a chave do Claude e o seu usuário do GitHub:
```
nano /opt/missao100/config.json
```
Conteúdo (troque os 2 valores):
```
{ "CLAUDE_API_KEY": "sk-ant-...", "GH_OWNER": "seu-usuario-github" }
```
(O resto — token da Meta, IG, GH_TOKEN — vem do `.credenciais.json`. Repo = `aprenda-nefro-posts`, branch `main`.)

## Passo 4 — Testar
Primeiro só a arte (não posta nada):
```
./venv/bin/python lib/slides.py 30
ls saida/dia-030/    # devem aparecer slide-01..slide-10.png
```
Depois um teste REAL de publicação (posta o episódio 30 no @aprendanefro — você pode apagar do feed depois):
```
./venv/bin/python run_dia.py 30
```
Conferiu no Instagram? Apague esse post de teste.

## Passo 5 — Ligar o cron (16h)
```
crontab -e
```
Cole a linha (fuso já deve ser America/Sao_Paulo, como no CCN):
```
0 16 * * * cd /opt/missao100 && ./venv/bin/python run_dia.py >> logs/cron.log 2>&1
```
Pronto: do dia 07/06 ao 14/09, todo dia 16h sai o carrossel automaticamente. Antes/depois da janela, não posta.

## Monitorar
```
tail -f /opt/missao100/logs/cron.log
```

## Erros comuns
- **GitHub upload failed**: GH_TOKEN sem permissão de escrita no repo `aprenda-nefro-posts` (gere um token com Contents: Read and write).
- **Graph API**: token expirado ou sem `instagram_content_publish`.
- **Imagem não aparece no post**: a URL do GitHub demorou a propagar — o script já espera; se persistir, aumentamos a folga.
