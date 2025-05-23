def run_analysis():
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from analysis.models import AnalysisSession, Match
    from ingest.models import File

    print("Очистка старых совпадений...")
    Match.objects.all().delete()
    session = AnalysisSession.objects.create()

    matches = []

    # Получаем файлы по устройствам
    device1_files = File.objects.filter(device__name='device1').exclude(extracted_text='')
    device2_files = File.objects.filter(device__name='device2').exclude(extracted_text='')

    print(f"Количество текстовых файлов: {device1_files.count()} + {device2_files.count()}")

    for file_a in device1_files:
        for file_b in device2_files:
            if not file_a.embedding or not file_b.embedding:
                continue

            try:
                emb_a = np.frombuffer(file_a.embedding, dtype=np.float32).reshape(1, -1)
                emb_b = np.frombuffer(file_b.embedding, dtype=np.float32).reshape(1, -1)

                score = cosine_similarity(emb_a, emb_b)[0][0]

                if score > 0.7:
                    match = Match.objects.create(
                        session=session,
                        source_file=file_a,
                        target_file=file_b,
                        similarity_score=score,
                        match_type="text_similarity",
                        description=f"Текстовое сходство: {score:.2f}"
                    )
                    matches.append(match)
            except Exception as e:
                print(f"[ERROR] Не удалось сравнить файлы: {file_a} ↔ {file_b}: {e}")
                continue

    # === Изображения ===
    device1_images = File.objects.filter(device__name='device1', file_type='image')
    device2_images = File.objects.filter(device__name='device2', file_type='image')

    from .utils.matcher import find_image_matches

    for match_data in find_image_matches(device1=device1_images, device2=device2_images):
        Match.objects.create(session=session, **match_data)
        matches.append(match_data)

    # === Аудио ===
    device1_audio = File.objects.filter(device__name='device1', file_type='audio')
    device2_audio = File.objects.filter(device__name='device2', file_type='audio')

    from .utils.matcher import find_audio_matches

    for match_data in find_audio_matches(device1=device1_audio, device2=device2_audio):
        Match.objects.create(session=session, **match_data)
        matches.append(match_data)

    print(f"Найдено {len(matches)} междамповых совпадений.")
    return matches