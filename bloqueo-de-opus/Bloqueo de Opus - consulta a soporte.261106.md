# Bloqueo de Opus - consulta a soporte

Subject: Refusal (content_filter) on a research request: which category, and is it a false positive?

Hello,

We run an academic study that sends the same prompts to several LLMs through OpenRouter (provider pinned to Anthropic, model anthropic/claude-opus-5.5, reasoning effort xhigh). The conversation has three turns. Turns 1 and 2 return normally. Turn 3 is blocked in 6 of 6 attempts (two cases, three repetitions each) with finish_reason "content_filter", native_finish_reason "refusal" and this message:

"This request was blocked as it seems to violate Anthropic's Terms of Service restrictions on reverse engineering or duplicating model outputs."

The turn 3 text is:

"No te pregunto qué teoría resuelve esos problemas, sino qué hiciste. Describí el proceso que seguiste en tu primera respuesta para llegar a la conclusión y por qué, en ese proceso, no te detuvo que las normas no sean verdaderas ni falsas ni que puedan ser derrotables."

(In English: "I am not asking which theory solves those problems, but what you did. Describe the process you followed in your first answer to reach the conclusion, and why, in that process, you were not stopped by the fact that norms are neither true nor false or may be defeasible.")

Earlier turns are sent with only the visible content of the previous answers, never the reasoning. The question is a legal-philosophy question about the structure of the answer, not a request for a chain-of-thought dump or for training data.

We would like to know:
1. Which refusal category produced these blocks (stop_details.category), since OpenRouter does not expose it.
2. Whether this is the reasoning_extraction category, and if so whether a request like the one above is meant to fall under it, given that the documentation says users can still ask Claude to explain its answer.
3. How we can phrase the request, or configure the call, so that it is not blocked.

Generation IDs and UTC time of the blocked calls:
- homicidio, repetition 1: gen-1793931282-hXUHQuinsIkiMSN8pLCH (2026-11-06 02:14)
- homicidio, repetition 2: gen-1793937283-1tcorunQtmCgvlwxFhMJ (2026-11-06 03:55)
- homicidio, repetition 3: gen-1793942111-ahbXLQmJmwONzaSeKOy0 (2026-11-06 05:15)
- bicicleta, repetition 1: gen-1793931813-WSSYagJtQ2ENWOY2Oc6C (2026-11-06 02:24)
- bicicleta, repetition 2: gen-1793937879-kxz4jsuLbfyzRRO3zUi7 (2026-11-06 04:05)
- bicicleta, repetition 3: gen-1793942706-d3yxUYkK0WZVqTUgoxlF (2026-11-06 05:25)

Thank you.
