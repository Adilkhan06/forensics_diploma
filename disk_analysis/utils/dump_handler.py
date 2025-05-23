# disk_analysis/utils/dump_handler.py

import os
from disk_analysis.utils.ewf_extractor import extract_files_from_e01  # твой предыдущий код
from disk_analysis.utils.carver import carve_images



def extract_files_from_dump(dump_path, name="device"):
    """
    Автоматически определяет тип дампа и извлекает файлы.
    Возвращает путь к извлеченным файлам
    """
    base_name = os.path.basename(dump_path).lower()

    # Если это E01 или RAW — используем dfvfs/pytsk3
    if base_name.endswith(".e01") or base_name.endswith(".raw") or base_name.endswith(".dd"):
        try:
            print(f"[INFO] Обнаружен дисковый образ: {dump_path}")
            extracted_dir = f"media/extracted/{name}"
            os.makedirs(extracted_dir, exist_ok=True)

            # Извлекаем файлы через dfvfs или pytsk3
            result_dir = extract_files_from_e01(dump_path, output_dir=extracted_dir)

            if not os.listdir(result_dir):  # если ничего не нашли
                print("[INFO] Файловая система не найдена, запускаю Carving")
                carve_images(dump_path, output_dir=os.path.join(extracted_dir, "carved"))
                result_dir = extracted_dir

            return result_dir

        except Exception as e:
            print(f"[ERROR] Не удалось обработать дисковый образ: {e}")
            # Резервное копирование — просто скопировать файлы, если не получилось монтировать
            return dump_path

    # Если это ZIP/TAR — стандартная обработка
    else:
        print(f"[INFO] Это архив ({base_name}), обработка как обычный дамп")
        return dump_path
