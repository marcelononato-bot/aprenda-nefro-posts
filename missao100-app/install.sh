#!/usr/bin/env bash
set -e
RAW="https://raw.githubusercontent.com/marcelononato-bot/aprenda-nefro-posts/main/missao100-app"
DEST=/opt/missao100
echo ">> Instalando Missao 100% (Instagram) em $DEST"
mkdir -p "$DEST/lib" "$DEST/assets" "$DEST/logs" "$DEST/saida"
for f in engine.py run_dia.py calendario.json DEPLOY-SERVIDOR.md lib/slides.py lib/caption.py lib/publicar_instagram.py assets/simbolo-missao100-ouro.png; do
  echo "  baixando $f"; curl -fsSL "$RAW/$f" -o "$DEST/$f"
done
echo ">> Criando ambiente Python (venv) + Pillow"
python3 -m venv "$DEST/venv"
"$DEST/venv/bin/pip" install -q --upgrade pip pillow
echo ">> Reaproveitando credenciais do Cafe com Nefro"
cp /opt/ccn/.credenciais.json "$DEST/.credenciais.json"
if [ ! -f "$DEST/config.json" ]; then
  printf '{\n  "CLAUDE_API_KEY": "COLE_AQUI_A_CHAVE_sk-ant",\n  "GH_OWNER": "marcelononato-bot"\n}\n' > "$DEST/config.json"
fi
echo ""
echo ">> PRONTO. Arquivos baixados, venv criado, credenciais copiadas."
echo ">> Falta 1 passo: colar a chave do Claude no arquivo $DEST/config.json"
