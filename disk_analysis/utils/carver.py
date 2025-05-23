# disk_analysis/utils/carver.py

import os
import re

JPEG_HEADER = rb'\xFF\xD8\xFF'
PNG_HEADER = b'\x89PNG\r\n\x1a\n'

def carve_images(raw_file_path, output_dir="media/carved_images"):
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    with open(raw_file_path, "rb") as f:
        data = f.read()

    # Поиск JPEG
    for match in re.finditer(JPEG_HEADER, data):
        offset = match.start()
        print(f"Найдено JPEG на смещении {offset}")
        carve_image(data, offset, output_dir, count, "jpg")
        count += 1

    # Поиск PNG
    for match in re.finditer(PNG_HEADER, data):
        offset = match.start()
        print(f"Найдено PNG на смещении {offset}")
        carve_image(data, offset, output_dir, count, "png")
        count += 1

    print(f"Найдено {count} файлов")


def carve_image(data, offset, output_dir, index, ext):
    # Примерный размер файла (можно улучшить через поиск конца файла)
    chunk = data[offset:offset + 1024 * 1024 * 10]  # 10 мб
    end_offset = chunk.find(b'\xFF\xD9')  # конец JPEG
    if end_offset != -1:
        carved_data = data[offset:offset + end_offset + 2]

        with open(os.path.join(output_dir, f"carved_{index}.{ext}"), "wb") as f:
            f.write(carved_data)