#!/bin/zsh
# Repeticiones 2 y 3 de las pruebas (TJS, 2026-11-05). Mismas carpetas que la repetición 1 (r2 y r3 junto a r1).
# La 3 solo se lanza si el saldo alcanza (ver chequeo). Sin supervisión; logs en ~/corridas-trasandino/log-rep{2,3}-*.txt
source ~/.zshrc
cd "$(dirname "$0")" || exit 1
FIN=~/corridas-trasandino/log-rep23-FIN.txt
caffeinate -dims -w $$ & disown
saldo() { curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/credits | python3 -c "import sys,json;d=json.load(sys.stdin)['data'];print(round(d['total_credits']-d['total_usage'],3))"; }
correr() {  # $1 modelo, $2 etiqueta, $3 tope USD (alarma, por comando), $4 repetición
  for caso in homicidio bicicleta; do
    python3 correr.py --caso $caso --preguntas p1 p2 p3 p4 --reps $4 --rep-desde $4 --modelos "$1" \
      --destino "20261105-2127-rep1-$2" --etiqueta "rep$4-$2" --tope-usd "$3" \
      >> ~/corridas-trasandino/log-rep$4-$2.txt 2>&1
  done
}
hacer_rep() {  # $1 repetición, $2 piso de saldo para Opus
  correr deepseek/deepseek-v4.1-flash-1017 deepseek 0.5 $1 &
  correr google/gemini-4-argon gemini 1 $1 &
  correr moonshotai/kimi-k3.1-pro kimi 1.5 $1 &
  correr z-ai/glm-5.3 glm 2 $1 &
  correr openai/gpt-6-astra astra 1.5 $1 &
  wait
  S=$(saldo)
  echo "Rep $1: saldo antes de Opus: $S USD ($(date))" >> $FIN
  if [ -z "$S" ] || [ "$(python3 -c "print(1 if float('${S:-0}')>=$2 else 0)")" != "1" ]; then
    echo "Rep $1: Opus NO lanzado: saldo insuficiente o ilegible ($S)." >> $FIN; return 1
  fi
  correr anthropic/claude-opus-5.5 opus 3 $1
  echo "Rep $1 terminada $(date)" >> $FIN
}
S0=$(saldo); echo "Inicio $(date); saldo $S0" >> $FIN
hacer_rep 2 4 || exit 1
S1=$(saldo); C=$(python3 -c "print(round($S0-$S1,3))")
echo "Costo de la rep 2: $C USD; saldo $S1" >> $FIN
if [ "$(python3 -c "print(1 if float('${S1:-0}')>=1.25*$C+0.5 and $C>0 else 0)")" != "1" ]; then
  echo "Rep 3 NO lanzada: saldo $S1 no alcanza para 1,25 x $C + 0,5." >> $FIN; exit 1
fi
hacer_rep 3 3
echo "Todo terminado $(date); saldo $(saldo)" >> $FIN
