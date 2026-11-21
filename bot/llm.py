"""AI chaqiruvlari: Groq (OpenAI-mos API) va Gemini. Model .env da "provayder:model" ko'rinishida.

Har chaqiruv: timeout, 429/5xx da qayta urinish, so'ng zaxira modelga o'tish (CLAUDE.md, F-band).
"""
import asyncio
import base64
import json
import logging
import re

import httpx

from . import config

log = logging.getLogger('lexnav.llm')
GROQ = 'https://api.groq.com/openai/v1'
GEMINI = 'https://generativelanguage.googleapis.com/v1beta'
RETRY_STATUS = {429, 500, 502, 503, 504}
_client: httpx.AsyncClient | None = None


class LLMError(RuntimeError):
    pass


def client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(60, connect=10))
    return _client


def _split(spec: str) -> tuple[str, str]:
    provider, _, model = spec.partition(':')
    if provider not in ('groq', 'gemini') or not model:
        raise LLMError(f'Noto\'g\'ri model sozlamasi: {spec}')
    return provider, model


async def _post(url: str, headers: dict, tries: int = 2, **kw) -> dict:
    for attempt in range(tries):
        try:
            r = await client().post(url, headers=headers, **kw)
        except httpx.TransportError as e:
            if attempt + 1 < tries:
                await asyncio.sleep(1.5)
                continue
            raise LLMError(f'tarmoq xatosi: {type(e).__name__}') from e
        if r.status_code in RETRY_STATUS and attempt + 1 < tries:
            try:
                wait = min(float(r.headers.get('retry-after', 0)), 8.0)
            except ValueError:
                wait = 0.0
            if r.status_code == 429 and wait > 6:  # uzoq kutish o'rniga zaxira modelga o'tamiz
                raise LLMError('HTTP 429: limit, zaxiraga o\'tiladi')
            await asyncio.sleep(max(wait, 1.5 * (attempt + 1)))
            continue
        if r.status_code >= 400:
            raise LLMError(f'HTTP {r.status_code}: {r.text[:200]}')
        try:
            return r.json()
        except ValueError as e:
            raise LLMError('JSON bo\'lmagan javob') from e
    raise LLMError('urinishlar tugadi')


async def _chat_once(spec: str, system: str, user: str, json_mode: bool, max_tokens: int,
                     image: bytes | None = None, mime: str = 'image/jpeg') -> str:
    provider, model = _split(spec)
    if provider == 'groq':
        if image is not None:
            raise LLMError('Groq modeli rasm qabul qilmaydi')
        body = {'model': model, 'max_tokens': max_tokens, 'temperature': 0.2,
                'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}
        if json_mode:
            body['response_format'] = {'type': 'json_object'}
        d = await _post(f'{GROQ}/chat/completions', {'Authorization': f'Bearer {config.GROQ_API_KEY}'}, json=body)
        return (d['choices'][0]['message'].get('content') or '').strip()
    parts: list[dict] = [{'text': user}]
    if image is not None:
        parts.insert(0, {'inline_data': {'mime_type': mime, 'data': base64.b64encode(image).decode()}})
    body = {'systemInstruction': {'parts': [{'text': system}]}, 'contents': [{'role': 'user', 'parts': parts}],
            'generationConfig': {'temperature': 0.2, 'maxOutputTokens': max_tokens}}
    if json_mode:
        body['generationConfig']['responseMimeType'] = 'application/json'
    d = await _post(f'{GEMINI}/models/{model}:generateContent', {'x-goog-api-key': config.GEMINI_API_KEY}, json=body)
    try:
        return ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts']).strip()
    except (KeyError, IndexError) as e:
        raise LLMError(f'Gemini bo\'sh javob: {str(d)[:200]}') from e


async def chat(system: str, user: str, *, model: str | None = None, json_mode: bool = False,
               max_tokens: int = 1500, image: bytes | None = None, mime: str = 'image/jpeg') -> str:
    """Asosiy model ishlamasa yoki bo'sh javob bersa — MODEL_FALLBACK ga o'tadi. Har model uchun 45 s chegara."""
    chain = [model or config.MODEL_STRONG]
    if config.MODEL_FALLBACK not in chain:
        chain.append(config.MODEL_FALLBACK)
    last: Exception | None = None
    for spec in chain:
        try:
            out = await asyncio.wait_for(_chat_once(spec, system, user, json_mode, max_tokens, image, mime), timeout=45)
            if out:
                return out
            last = LLMError(f'{spec}: bo\'sh javob')
        except asyncio.TimeoutError:
            last = LLMError(f'{spec}: 45 s ichida javob bermadi')
        except (LLMError, KeyError, IndexError, ValueError) as e:  # buzilgan javob ham zaxiraga o'tishga sabab
            last = e if isinstance(e, LLMError) else LLMError(f'{spec}: javob formati xato ({type(e).__name__})')
        log.warning('Model ishlamadi, keyingisiga o\'tilmoqda: %s | %s', spec, last)
    raise LLMError(f'Barcha modellar ishlamadi: {last}')


def parse_json(text: str) -> dict:
    """Model ```json ... ``` bilan o'rab yuborsa ham JSON ni ajratib oladi."""
    m = re.search(r'\{.*\}', text, re.S)
    if not m:
        raise LLMError(f'JSON topilmadi ({len(text)} belgi)')  # foydalanuvchi matni logga tushmasin
    try:
        return json.loads(m.group(0))
    except ValueError as e:
        raise LLMError(f'JSON buzilgan ({len(text)} belgi)') from e


# O'zbek (lotin/kirill) va rus matnida bo'lmaydigan harflar: qozoq, ozarbayjon, turk, arab yozuvi.
# 2026-11-20 sinovida Whisper o'zbekcha ovozni aynan shu tillarga o'girib yuborgan (auditor topilmasi).
FOREIGN = re.compile(r'[ңұүіәөһəışçğöüا-ي]')
STT_PROMPT = "Bu audiodagi nutqni o'zbek tilida (lotin yozuvida) so'zma-so'z yozib ber. Ruscha so'zlarni o'zgartirma. Faqat matnni qaytar."


def _audio_mime(filename: str) -> str:
    ext = filename.rsplit('.', 1)[-1].lower()
    return {'ogg': 'audio/ogg', 'oga': 'audio/ogg', 'opus': 'audio/ogg', 'mp3': 'audio/mp3', 'm4a': 'audio/mp4',
            'mp4': 'audio/mp4', 'wav': 'audio/wav', 'amr': 'audio/amr', 'aac': 'audio/aac', 'webm': 'audio/webm'}.get(ext, 'audio/ogg')


async def _transcribe_once(spec: str, audio: bytes, filename: str) -> str:
    provider, model = _split(spec)
    if provider == 'gemini':
        body = {'contents': [{'role': 'user', 'parts': [
            {'inline_data': {'mime_type': _audio_mime(filename), 'data': base64.b64encode(audio).decode()}},
            {'text': STT_PROMPT}]}], 'generationConfig': {'temperature': 0}}
        d = await _post(f'{GEMINI}/models/{model}:generateContent', {'x-goog-api-key': config.GEMINI_API_KEY}, json=body)
        try:
            return ''.join(p.get('text', '') for p in d['candidates'][0]['content']['parts']).strip()
        except (KeyError, IndexError) as e:
            raise LLMError('Gemini bo\'sh transkripsiya') from e
    d = await _post(f'{GROQ}/audio/transcriptions', {'Authorization': f'Bearer {config.GROQ_API_KEY}'},
                    files={'file': (filename, audio)},
                    data={'model': model, 'temperature': '0', 'language': 'uz',
                          'prompt': "Assalomu alaykum. Menga yordam bering, qayerga murojaat qilishni bilmayman."})
    return (d.get('text') or '').strip()


async def transcribe(audio: bytes, filename: str) -> str:
    """Ovoz → matn. Zanjir: MODEL_STT (Gemini transcribe) → MODEL_STT_FALLBACK → Groq Whisper (language=uz).
    Natijada begona yozuv harflari bo'lsa (qozoq/ozarbayjon/arab), keyingi modelga o'tiladi."""
    chain = [config.MODEL_STT, config.MODEL_STT_FALLBACK, 'groq:whisper-large-v3']
    last: Exception | None = None
    for spec in dict.fromkeys(s for s in chain if s):
        try:
            text = await asyncio.wait_for(_transcribe_once(spec, audio, filename), timeout=45)
        except (LLMError, asyncio.TimeoutError) as e:
            last = e
            log.warning('STT ishlamadi: %s | %s', spec, type(e).__name__)
            continue
        if text and not FOREIGN.search(text.lower()):
            return text
        last = LLMError(f'{spec}: o\'zbekcha bo\'lmagan matn')
        log.warning('STT natijasi o\'zbekcha emas (%s), keyingi model', spec)
    raise LLMError(f'Ovozni o\'girib bo\'lmadi: {last}')
