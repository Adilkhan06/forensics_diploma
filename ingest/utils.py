import os
from .models import Device, File


def process_dump(device_name, dump_folder):
    device = Device.objects.create(name=device_name, dump_path=dump_folder)

    for root, dirs, files in os.walk(dump_folder):
        for file in files:
            full_path = os.path.join(root, file)
            # TODO: добавь логику определения типа файла, размера, MIME и т.д.
            File.objects.create(
                device=device,
                file_path=full_path,
                file_type="unknown",  # можно улучшить
                size=os.path.getsize(full_path),
                created_at=...  # datetime
            )