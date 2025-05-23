import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .similarity import calculate_cosine_similarity, perceptual_image_hash
from .gemini_client import get_gemini_summary

def find_text_matches(threshold=0.7):
    files_device1 = File.objects.filter(device__name='device1').exclude(extracted_text='')
    files_device2 = File.objects.filter(device__name='device2').exclude(extracted_text='')

    for file_a in files_device1:
        for file_b in files_device2:
            if not file_a.embedding or not file_b.embedding:
                continue

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

def find_audio_matches(device1=None, device2=None):
    if device1 is None:
        device1 = File.objects.filter(device__name='device1', file_type='audio').exclude(extracted_text='')
    if device2 is None:
        device2 = File.objects.filter(device__name='device2', file_type='audio').exclude(extracted_text='')

    results = []

    for file_a in device1:
        for file_b in device2:
            if not file_a.embedding or not file_b.embedding:
                continue

            emb_a = np.frombuffer(file_a.embedding, dtype=np.float32).reshape(1, -1)
            emb_b = np.frombuffer(file_b.embedding, dtype=np.float32).reshape(1, -1)

            score = calculate_cosine_similarity(emb_a, emb_b)

            if score > 0.75:
                results.append({
                    "source_file": file_a,
                    "target_file": file_b,
                    "similarity_score": score,
                    "match_type": "audio_similarity",
                    "description": f"Аудио совпадение: {score:.2f}"
                })

    return results

def find_image_matches(device1=None, device2=None, threshold=0.7):
    if device1 is None:
        device1 = File.objects.filter(device__name='device1', file_type='image')
    if device2 is None:
        device2 = File.objects.filter(device__name='device2', file_type='image')

    results = []

    for file_a in device1:
        for file_b in device2:
            if not file_a.embedding or not file_b.embedding:
                continue

            try:
                emb_a = np.frombuffer(file_a.embedding, dtype=np.float32)
                emb_b = np.frombuffer(file_b.embedding, dtype=np.float32)

                score = calculate_cosine_similarity(emb_a, emb_b)

                if score > threshold:
                    results.append({
                        "source_file": file_a,
                        "target_file": file_b,
                        "similarity_score": score,
                        "match_type": "image_similarity",
                        "description": f"Сходство изображений: {score:.2f}"
                    })
            except Exception as e:
                print(f"[ERROR] Не удалось сравнить изображения: {e}")

    return results

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
