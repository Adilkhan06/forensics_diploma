# ingest/utils/file_processor.py

import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import whisper
from sentence_transformers import SentenceTransformer
from tensorflow.keras.models import load_model


text_model = SentenceTransformer('all-MiniLM-L6-v2')

image_model = load_model('models/image_embedding_model.h5')  # путь должен быть правильным

audio_model = whisper.load_model("base")

def get_file_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.txt', '.docx', '.pdf']:
        return 'document'
    elif ext in ['.jpg', '.jpeg', '.png']:
        return 'image'
    elif ext in ['.mp4', '.avi']:
        return 'video'
    elif ext in ['.mp3', '.wav']:
        return 'audio'
    else:
        return 'unknown'


def extract_text_from_document(file_path):
    ext = os.path.splitext(file_path)[1]
    try:
        if ext == '.pdf':
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() for page in reader.pages])
        elif ext == '.docx':
            from docx import Document
            doc = Document(file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Не удалось прочитать документ {file_path}: {e}")
        return None


def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"[ERROR] OCR не удался для {image_path}: {e}")
        return None


def extract_embedding_from_image(image_path):
    try:
        img = cv2.imread(image_path)
        img = cv2.resize(img, (224, 224)) / 255.0
        embedding = image_model.predict(np.expand_dims(img, axis=0))
        return embedding.tobytes()
    except Exception as e:
        print(f"[ERROR] Не удалось получить эмбеддинг для изображения {image_path}: {e}")
        return None


def extract_audio_text(audio_path):
    try:
        result = audio_model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"[ERROR] ASR не удался для аудио {audio_path}: {e}")
        return None


def extract_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        if count % 30 == 0:
            frames.append(frame)
        count += 1
    cap.release()
    return frames


def extract_text_from_video(video_path, every_n=30):
    import cv2
    import tempfile

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERROR] Не удалось открыть видеофайл:", video_path)
        return ""

    count = 0
    all_text = ""
    temp_dir = tempfile.gettempdir()

    print(f"[INFO] Используется временная папка: {temp_dir}")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("[INFO] Конец видео или ошибка чтения.")
            break

        if count % every_n == 0:
            temp_path = os.path.join(temp_dir, f"frame_{count}.jpg")
            print(f"[DEBUG] Сохраняю кадр {count} как {temp_path}")

            cv2.imwrite(temp_path, frame)

            if not os.path.exists(temp_path):
                print(f"[ERROR] Кадр {temp_path} не был сохранён!")
                count += 1
                continue

            try:
                text = extract_text_from_image(temp_path)
                print(f"[OCR] Найденный текст: {text[:50]}..." if text else "[OCR] Текст не найден")
                if text:
                    all_text += text + " "
                os.remove(temp_path)
            except Exception as e:
                print(f"[ERROR] Не удалось обработать кадр {count}: {e}")

        count += 1

    cap.release()
    print(f"[INFO] Обработка завершена. Итоговый текст: {all_text[:100]}...")
    return all_text.strip()


def get_text_embedding(text):
    if not text or len(text.strip()) < 5:
        return None
    try:
        emb = text_model.encode([text])
        return emb.tobytes()
    except Exception as e:
        print(f"[ERROR] Не удалось создать эмбеддинг для текста: {e}")
        return None