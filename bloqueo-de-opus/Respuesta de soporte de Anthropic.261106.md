# Respuesta de soporte de Anthropic

Respuesta del soporte de Anthropic a la consulta sobre el bloqueo de Opus 5.5 en la repregunta (6 de noviembre de 2026). La consulta está en `Bloqueo de Opus - consulta a soporte.261106.md`.

## Datos del mail

- De: Jasper, Anthropic Support (`support@mail.anthropic.com`, enviado por `outbound.intercom.mail.anthropic.com`, firmado por `mail.anthropic.com`).
- Para: la cuenta de TJS. Fecha: 6 de noviembre de 2026, 20:16 (hora de Argentina).
- Asunto: "Re: Content filter refusal analysis".
- Seguridad: TLS estándar.

## Texto literal

> Hi Tob,
>
> Thanks for reaching out to Anthropic Support.
>
> The explanation text in the block message isn't a stable identifier. The category itself is in stop_details.category on a native Messages API response, which you mention OpenRouter doesn't expose. The wording you received matches what we associate with the reasoning_extraction category, which our documentation describes as: "The request asks the model to reproduce its internal reasoning in the response text."
>
> That category can also catch benign work, and prompts that ask Claude to show its reasoning can trigger it. This category has no recommended fallback model, so the documentation advises changing the prompt rather than retrying the same request. Options are rewording the prompt so it doesn't ask for the model's reasoning, changing the input format, or using structured outputs. If a reworded request is still declined, send us the request ID and we'll look into it.
>
> Feel free to write back if you need anything else.
>
> Kind regards,
> Jasper
