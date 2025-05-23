import os
import json
from PIL import Image
from PIL.ExifTags import TAGS
from docx import Document
from PyPDF2 import PdfReader
import mutagen  # Для MP3 метаданных

from ingest.utils.file_processor import get_file_type


def extract_metadata(file_path):
    """
    Извлекает метаданные из файла по типу
    Возвращает словарь с метаданными
    """
    file_type = get_file_type(file_path)

    if file_type == 'image':
        return extract_image_metadata(file_path)
    elif file_type == 'document':
        return extract_document_metadata(file_path)
    elif file_type == 'audio':
        return extract_audio_metadata(file_path)
    elif file_type == 'video':
        return extract_video_metadata(file_path)
    else:
        return {"error": "Неизвестный формат файла"}


def extract_image_metadata(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        metadata = {}

        if exif_data:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = str(value)

        # Дополнительные метаданные через Image.info
        metadata.update({
            "format": image.format,
            "size": image.size,
            "mode": image.mode,
            "info": str(image.info)
        })

        return metadata
    except Exception as e:
        return {"error": f"Не удалось извлечь метаданные изображения: {e}"}


def extract_document_metadata(doc_path):
    ext = os.path.splitext(doc_path)[1].lower()

    if ext == '.pdf':
        try:
            with open(doc_path, 'rb') as f:
                reader = PdfReader(f)
                info = reader.metadata
                if info:
                    return {
                        "title": info.title,
                        "author": info.author,
                        "creator": info.creator,
                        "producer": info.producer,
                        "subject": info.subject,
                        "creation_date": info.creation_date,
                        "modification_date": info.modification_date
                    }
                return {"status": "no metadata"}
        except Exception as e:
            return {"error": f"Не удалось прочитать PDF-метаданные: {e}"}

    elif ext == '.docx':
        try:
            doc = Document(doc_path)
            core_props = doc.core_properties
            return {
                "title": core_props.title,
                "author": core_props.author,
                "created": str(core_props.created),
                "modified": str(core_props.modified),
                "category": core_props.category,
                "subject": core_props.subject,
                "language": core_props.language
            }
        except Exception as e:
            return {"error": f"Не удалось прочитать DOCX-метаданные: {e}"}
    else:
        return {"error": "Формат документа не поддерживается"}


def extract_audio_metadata(audio_path):
    try:
        audio = mutagen.File(audio_path)
        if not audio:
            return {"error": "Нет доступных метаданных"}

        tags = {}
        for k, v in audio.items():
            tags[k] = str(v)

        return tags
    except Exception as e:
        return {"error": f"Не удалось прочитать аудио-метаданные: {e}"}


def extract_video_metadata(video_path):
    # Пока заглушка — можно использовать ffmpeg или MediaInfo
    return {
        "warning": "Метаданные видео пока не реализованы",
        "file": video_path
    }