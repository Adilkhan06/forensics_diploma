import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .similarity import calculate_cosine_similarity, perceptual_image_hash
from .gemini_client import get_gemini_summary

def find_text_matches(threshold=0.7):
    from ingest.models import File

    text_files = File.objects.exclude(extracted_text__isnull=True).exclude(extracted_text='')

    for file_a in text_files:
        for file_b in text_files:
            if file_a.id >= file_b.id:
                continue  # избегаем дублей

            try:
                emb_a = np.frombuffer(file_a.embedding, dtype=np.float32)
                emb_b = np.frombuffer(file_b.embedding, dtype=np.float32)

                score = calculate_cosine_similarity(emb_a, emb_b)

                if score > threshold:
                    yield {
                        "source": file_a,
                        "target": file_b,
                        "score": score,
                        "type": "text_similarity"
                    }
            except Exception as e:
                print(f"[ERROR] Не удалось сравнить файлы: {file_a}, {file_b} → {e}")
                continue

def find_audio_matches(threshold=0.7):
    from ingest.models import File

    audio_files = File.objects.filter(file_type='audio').exclude(extracted_text__isnull=True).exclude(extracted_text='')

    for file_a in audio_files:
        for file_b in audio_files:
            if file_a.id >= file_b.id:
                continue
            if file_a.embedding and file_b.embedding:
                try:
                    emb_a = np.frombuffer(file_a.embedding, dtype=np.float32)
                    emb_b = np.frombuffer(file_b.embedding, dtype=np.float32)

                    score = calculate_cosine_similarity(emb_a, emb_b)

                    if score > threshold:
                        yield {
                            "source": file_a,
                            "target": file_b,
                            "score": score,
                            "type": "audio_similarity"
                        }
                except Exception as e:
                    print(f"[ERROR] Не удалось сравнить аудио: {e}")

def find_image_matches(threshold=0.7):
    from ingest.models import File

    image_files = File.objects.filter(file_type='image').exclude(extracted_text__isnull=True).exclude(extracted_text='')

    for file_a in image_files:
        for file_b in image_files:
            if file_a.id >= file_b.id:
                continue

            if file_a.embedding and file_b.embedding:
                try:
                    emb_a = np.frombuffer(file_a.embedding, dtype=np.float32)
                    emb_b = np.frombuffer(file_b.embedding, dtype=np.float32)

                    score = calculate_cosine_similarity(emb_a, emb_b)

                    if score > threshold:
                        yield {
                            "source": file_a,
                            "target": file_b,
                            "score": score,
                            "type": "image_similarity"
                        }
                except Exception as e:
                    print(f"[ERROR] Не удалось сравнить изображения: {e}")

def collect_analysis_data():
    from analysis.models import Match

    matches = Match.objects.all()
    result = []

    for match in matches:
        result.append(f"""
        Совпадение: {match.source_file} ↔ {match.target_file}
        Тип: {match.match_type}
        Устройства: {match.source_file.device.name} ↔ {match.target_file.device.name}
        Сходство: {match.similarity_score:.2f}
        Описание: {match.description}
        """)

    return "\n".join(result)
