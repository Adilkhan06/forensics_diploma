import os
import tarfile
import zipfile

from django.shortcuts import render

from analysis.models import Match, AnalysisSession
from analysis.tasks import run_analysis
from disk_analysis.utils.dump_handler import extract_files_from_dump
from .models import Device, File

from .utils.file_processor import (
    get_file_type,
    extract_text_from_document,
    extract_text_from_image,
    extract_text_from_video,
    extract_audio_text,
    get_text_embedding,
    extract_embedding_from_image
)

def upload_success_view(request):
    return render(request, 'ingest/upload_success.html')

def upload_dumps_view(request):
    if request.method == 'POST':
        device1 = request.FILES.get('device1')
        device2 = request.FILES.get('device2')

        if not device1 or not device2:
            return render(request, 'ingest/upload.html', {'error': 'Выберите оба дампа'})

        print("Очистка старых данных...")
        File.objects.all().delete()
        Device.objects.all().delete()

        # Match.objects.all().delete()
        # AnalysisSession.objects.all().delete()

        # Обработка первого дампа
        dump1_path = handle_uploaded_file(device1)
        dump2_path = handle_uploaded_file(device2)

        # Извлечение файлов из дампов (поддержка .zip и .E01/.raw)
        device1_extracted = extract_files_from_dump(dump1_path, name='device1')
        device2_extracted = extract_files_from_dump(dump2_path, name='device2')

        # Создаем устройства и связываем с распакованными файлами
        device1_obj = Device.objects.create(name='device1', dump_path=device1_extracted)
        device2_obj = Device.objects.create(name='device2', dump_path=device2_extracted)

        process_dump_files(device1_obj.id)
        process_dump_files(device2_obj.id)

        run_analysis()

        return render(request, 'ingest/upload.html', {
            'analysis_done': True,
            'message': '✅ Дампы загружены, файлы извлечены'
        })

    return render(request, 'ingest/upload.html')

def handle_uploaded_file(f):
    upload_dir = 'media/uploads/'
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # Распаковываем только если это ZIP
    if file_path.lower().endswith('.zip'):
        extract_dir = file_path.replace('.zip', '')
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir
    elif file_path.lower().endswith(('.tar', '.tar.gz')):
        extract_dir = file_path.replace('.tar', '').replace('.gz', '')
        with tarfile.open(file_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_dir)
        return extract_dir
    else:
        # Если это RAW/E01 — просто возвращаем путь
        return file_path

def extract_archive(path, extract_to):
    if path.endswith('.zip'):
        import zipfile
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif path.endswith(('.tar', '.tar.gz')):
        import tarfile
        with tarfile.open(path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_to)

def process_dump_files(device_id):
    device = Device.objects.get(id=device_id)
    dump_path = device.dump_path

    for root, dirs, files in os.walk(dump_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            rel_path = os.path.relpath(file_path, dump_path)

            db_file, created = File.objects.get_or_create(
                device=device,
                file_path=file_path,
                defaults={
                    'relative_path': rel_path,
                    'file_type': get_file_type(file_path),
                    'mime_type': 'application/octet-stream',
                    'size': os.path.getsize(file_path),
                }
            )

            if not created:
                db_file.relative_path = rel_path
                db_file.save()

            try:
                size = os.path.getsize(file_path)
                db_file.size = size
            except Exception:
                pass

            db_file.file_type = get_file_type(file_path)

            extracted_text = None
            embedding = None

            if db_file.file_type == 'document':
                extracted_text = extract_text_from_document(file_path)
            elif db_file.file_type == 'image':
                extracted_text = extract_text_from_image(file_path)
                db_file.extracted_text = extracted_text
                db_file.embedding = extract_embedding_from_image(file_path)
            elif db_file.file_type == 'audio':
                extracted_text = extract_audio_text(file_path)
            elif db_file.file_type == 'video':
                extracted_text = extract_text_from_video(file_path)

            if extracted_text:
                db_file.extracted_text = extracted_text
                db_file.embedding = get_text_embedding(extracted_text)
            elif embedding:
                db_file.embedding = embedding

            db_file.save()

        print(f"[INFO] Устройство '{device.name}' обработано. Найдено файлов: {len(files)}")