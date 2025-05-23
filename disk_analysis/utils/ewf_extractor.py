# disk_analysis/utils/ewf_extractor.py

import os
import pyewf
import pytsk3
from django.core.files.storage import default_storage


def extract_files_from_e01(evidence_path, output_dir=None):
    """
    evidence_path — путь к .E01 или .raw
    output_dir — папка для извлечения файлов (если не указано, будет создана автоматически)
    """

    # Автоматически задаем output_dir, если его нет
    if output_dir is None:
        output_dir = "media/extracted/"

    os.makedirs(output_dir, exist_ok=True)

    try:
        # Извлечение через libewf
        filenames = pyewf.glob(evidence_path)
        ewf_handle = pyewf.handle()
        ewf_handle.open(filenames)

        img_info = pytsk3.Img_Info(ewf_handle)

        # Открываем файловую систему
        fs_info = pytsk3.FS_Info(img_info)
        print(f"Файловая система: {fs_info.info.ftype}")
        print(f"Размер блока: {fs_info.info.block_size}")

        def process_directory(directory, path="/", output_root=output_dir):
            for entry in directory:
                try:
                    full_path = os.path.join(path, entry.info.name.name.decode('utf-8'))

                    # Если это директория → рекурсивно обрабатываем
                    if entry.info.name.type == pytsk3.TSK_FS_NAME_TYPE_DIR:
                        sub_dir = entry.as_directory()
                        process_directory(sub_dir, full_path, output_root)

                    # Если это регулярный файл → извлекаем
                    elif entry.info.name.type == pytsk3.TSK_FS_NAME_TYPE_REG:
                        rel_output_dir = os.path.join(output_root, path.strip("/").replace("/", "_"))
                        os.makedirs(rel_output_dir, exist_ok=True)

                        file_path = os.path.join(rel_output_dir, entry.info.name.name.decode('utf-8'))

                        print(f"[INFO] Извлекаю: {full_path} → {file_path}")

                        with open(file_path, "wb") as f:
                            f.write(entry.read_random(0, entry.info.meta.size))

                except Exception as e:
                    print(f"[ERROR] Не удалось обработать файл {entry.info.name.name}: {e}")

        root_dir = fs_info.open_dir("/")
        process_directory(root_dir)

        return output_dir

    except Exception as e:
        print(f"[ERROR] Не удалось открыть образ: {e}")
        raise