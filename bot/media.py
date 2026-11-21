"""Media → matn. Fayl diskka yozilmaydi: xotirada yuklanadi, matnga o'giriladi va tashlab yuboriladi (CLAUDE.md, 6-qoida)."""
import io
import logging
from dataclasses import dataclass

from aiogram import Bot
from aiogram.types import Message

from . import config, llm

log = logging.getLogger('lexnav.media')

VISION_PROMPT = (
    "Bu rasm fuqaro huquqiy maslahat uchun yuborgan skrinshot yoki hujjat. "
    "1) Rasmdagi barcha matnni (SMS, chat, hujjat) aynan, o'zgartirmasdan ko'chir; yuboruvchi raqam yoki nomni ham yoz. "
    "2) Keyin 'Tasvir:' deb boshlab, 1–2 jumlada rasmda nima ko'rinayotganini o'zbek tilida (lotin) yoz. "
    "Hech qanday huquqiy xulosa chiqarma."
)
VISION_SYSTEM = "Sen rasmdagi matnni aniq ko'chiruvchi yordamchisan. Faqat ko'rganingni yoz, o'ylab topma."


class MediaError(RuntimeError):
    pass


@dataclass
class Extracted:
    kind: str   # text | voice | audio | image | document
    text: str


async def _download(bot: Bot, file_id: str) -> bytes:
    buf = io.BytesIO()
    await bot.download(file_id, destination=buf)
    return buf.getvalue()


async def extract(bot: Bot, m: Message) -> Extracted:
    if m.text:
        return Extracted('text', m.text)
    caption = (m.caption or '').strip()
    audio_doc = m.document if m.document and (m.document.mime_type or '').startswith('audio/') else None
    if m.voice or m.audio or m.video_note or m.video or audio_doc:
        f = m.voice or m.audio or m.video_note or m.video or audio_doc
        name = getattr(f, 'file_name', None) or ('voice.ogg' if m.voice else 'audio.mp4' if (m.video or m.video_note) else 'audio.mp3')
        data = await _download(bot, f.file_id)
        text = await llm.transcribe(data, name)
        del data
        if not text:
            raise MediaError('Ovozdan matn ajratib bo\'lmadi')
        kind = 'voice' if m.voice else 'audio'
        return Extracted(kind, (caption + '\n' if caption else '') + text)
    image_id, mime = None, 'image/jpeg'
    if m.photo:
        image_id = m.photo[-1].file_id
    elif m.document and (m.document.mime_type or '').startswith('image/'):
        image_id, mime = m.document.file_id, m.document.mime_type
    if image_id:
        data = await _download(bot, image_id)
        text = await llm.chat(VISION_SYSTEM, VISION_PROMPT, model=config.MODEL_VISION, image=data, mime=mime, max_tokens=1200)
        del data
        return Extracted('image', (caption + '\n' if caption else '') + text)
    if m.document and (m.document.mime_type or '').startswith('text/'):
        data = await _download(bot, m.document.file_id)
        return Extracted('document', data.decode('utf-8', 'replace')[:8000])
    raise MediaError('Qo\'llanmaydigan fayl turi')
