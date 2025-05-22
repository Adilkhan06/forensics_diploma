import google.generativeai as genai
from django.conf import settings

# Настройка Gemini API
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", None)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY не установлен")

def get_gemini_summary(text):
    if not GEMINI_API_KEY:
        return "Ошибка: Gemini API ключ не найден"

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Ниже приведены результаты анализа цифровых следов между двумя устройствами.
    Твоя задача — проанализировать эти данные и подготовить структурированный отчет на русском языке.
    Ответ должен быть понятен юристам, экспертам и техническим специалистам.
    
    Формат вывода:
    - Простой текст (без markdown)
    - Разделы с заголовками через пробел и тире, например: 1. Краткое описание совпадений
    - Подразделы и пункты оформлять через перенос строки, без звездочек и маркированных списков
    - Используй точные названия файлов и типов совпадений из данных
    
    Данные:
    {text}
    
    Отчет должен содержать:
    1. Краткое описание совпадений
    2. Вывод о возможной связи между устройствами
    3. Рекомендации по дальнейшему анализу
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[ERROR] Не удалось получить ответ от Gemini: {e}"