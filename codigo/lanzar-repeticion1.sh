#!/bin/zsh
# Primera repetición de las pruebas (TJS, 2026-11-05). Seis modelos, dos casos, p1-p4, 1 repetición.
# Un modelo por comando, otro --destino cada uno; sin --max-tokens; --tope-usd solo como alarma.
# Baratos en paralelo; Opus al final (después de que terminen los demás).
# Uso: zsh lanzar-repeticion1.sh   (dejar la compu enchufada; caffeinate evita que duerma)
source ~/.zshrc
cd "$(dirname "$0")" || exit 1
mkdir -p ~/corridas-trasandino
F=$(date +%Y%m%d-%H%M)
correr() {  # $1 = id de modelo, $2 = etiqueta, $3 = tope USD
  for caso in homicidio bicicleta; do
    python3 correr.py --caso $caso --preguntas p1 p2 p3 p4 --reps 1 --modelos "$1" \
      --destino "$F-rep1-$2" --etiqueta "rep1-$2" --tope-usd "$3" \
      >> ~/corridas-trasandino/log-rep1-$2.txt 2>&1
  done
}
caffeinate -dims -w $$ & disown
correr deepseek/deepseek-v4.1-flash-1017 deepseek 2 &
correr google/gemini-4-argon gemini 3 &
correr moonshotai/kimi-k3.1-pro kimi 4 &
correr z-ai/glm-5.3 glm 4 &
correr openai/gpt-6-astra astra 6 &
wait
# Chequeo de saldo antes de Opus: si queda menos que su tope (9 USD), no lo lanza.
SALDO=$(curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/credits | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print(round(d['total_credits']-d['total_usage'],2))")
echo "Saldo antes de Opus: $SALDO USD ($(date))" >> ~/corridas-trasandino/log-rep1-FIN.txt
if [ -z "$SALDO" ] || [ "$(python3 -c "print(1 if float('${SALDO:-0}')>=9 else 0)")" != "1" ]; then
  echo "Opus NO lanzado: saldo insuficiente o ilegible ($SALDO). Lanzarlo a mano cuando se recargue." >> ~/corridas-trasandino/log-rep1-FIN.txt
  exit 1
fi
correr anthropic/claude-opus-5.5 opus 9
echo "Terminado $(date)" >> ~/corridas-trasandino/log-rep1-FIN.txt
