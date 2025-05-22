def run_analysis():
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    from analysis.models import AnalysisSession, Match
    from ingest.models import File
    from .utils.matcher import find_image_matches


    print("Очистка старых совпадений...")
    AnalysisSession.objects.all().delete()

    session = AnalysisSession.objects.create()
    matches = []


    text_files = File.objects.exclude(extracted_text__isnull=True).exclude(extracted_text='')

    for match_data in find_image_matches():
        Match.objects.create(
            session=session,
            source_file=match_data["source"],
            target_file=match_data["target"],
            similarity_score=match_data["score"],
            match_type=match_data["type"],
            description=f"Сходство изображений: {match_data['score']:.2f}"
        )

    for file_a in text_files:
        for file_b in text_files:
            if file_a.id >= file_b.id:
                continue

            try:

                emb_a = np.frombuffer(file_a.embedding, dtype=np.float32)
                emb_b = np.frombuffer(file_b.embedding, dtype=np.float32)


                score = cosine_similarity(emb_a.reshape(1, -1), emb_b.reshape(1, -1))[0][0]

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

    # === Аудио сравнение (если реализовано) ===
    audio_files = File.objects.filter(file_type='audio').exclude(extracted_text='')
    if audio_files.exists():
        from .utils.matcher import find_audio_matches
        for match_data in find_audio_matches():
            print(f"[DEBUG] Совпадение: {match_data['source']} ↔ {match_data['target']}")
            if not match_data["source"] or not match_data["target"]:
                print("[ERROR] source или target равен None")
                continue

            match = Match.objects.create(**{
                'session': session,
                'source_file': match_data["source"],
                'target_file': match_data["target"],
                'similarity_score': match_data["score"],
                'match_type': match_data["type"],
                'description': f"Аудио совпадение: {match_data['score']:.2f}"
            })
            matches.append(match)

    text_files = File.objects.exclude(extracted_text__isnull=True).exclude(extracted_text='')

    print(f"Количество текстовых файлов для анализа: {text_files.count()}")
    for f in text_files:
        print(f"{f} → длина текста: {len(f.extracted_text) if f.extracted_text else 0}")
    print(f"Найдено {len(matches)} совпадений.")
    return matches