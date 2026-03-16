import requests
from duckduckgo_search import DDGS
import json

class BookAnalyzer:
    def __init__(self, mistral_api_key):
        """
        Инициализация анализатора с ключом Mistral API
        """
        self.mistral_api_key = mistral_api_key
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"

    def search_duckduckgo(self, query, max_results=4):
        """
        Поиск информации через DuckDuckGo (без ключей)
        """
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, region='ru-ru', max_results=max_results):
                    if r.get('body'):
                        results.append({
                            'title': r.get('title', ''),
                            'body': r.get('body', ''),
                            'href': r.get('href', '')
                        })
            return results
        except Exception as e:
            return []
    
    def analyze_book(self, book): 
        """
        Полный анализ книги с поиском в интернете
        """

        # поисковые запросы
        queries = [
            f"{book} краткое содержание анализ",
            f"{book} главные герои проблема",
            f"{book} рецензия критика"
        ]

        # собираем информацию
        all_info = []
        sources = []

        for query in queries:

            results = self.search_duckduckgo(query)

            for r in results:
                if r['body'] and len(r['body']) > 100:  # только содержательные результаты
                    # добавляем заголовок и текст
                    all_info.append(f"📌 {r['title']}")
                    all_info.append(r['body'])
                    all_info.append("---")
                    sources.append(r.get('href', ''))

        # если мало информации, пробуем общий запрос
        if len(all_info) < 3:
            results = self.search_duckduckgo(f"{book} книга", max_results=5)
            for r in results:
                if r['body']:
                    all_info.append(f"{r['title']}")
                    all_info.append(r['body'])
                    all_info.append("---")

        # формируем контекст
        internet_context = "\n".join(all_info) if all_info else "Информация из интернета не найдена."

        # системный промпт
        system_prompt = """Ты — профессиональный литературный критик и аналитик с филологическим образованием.
Твоя задача — анализировать книги любых жанров на основе информации из интернета и собственных знаний.
Отвечай структурированно, профессионально, но доступно. Используй русский язык.
Строго запрещено использовать различные приемы для визуального изменения текста, такие как жирный текст, курсивный и т.д."""

        user_prompt = f"""Проанализируй книгу "{book}".

ИНФОРМАЦИЯ ИЗ ИНТЕРНЕТА:
{internet_context[:12000]}

ИНСТРУКЦИЯ:
1. СНАЧАЛА определи тип книги: художественная (роман, повесть, рассказ, поэзия, драма) или нехудожественная (научная, учебная, биография, документальная, бизнес-литература, публицистика, философия).
2. В зависимости от типа книги, используй соответствующий шаблон анализа:

ЕСЛИ КНИГА ХУДОЖЕСТВЕННАЯ:
1. ПРОБЛЕМА: Какая основная проблема/конфликт подняты в книге?
2. ГЛАВНЫЙ ТЕЗИС: Какую главную мысль проводит автор через сюжет и образы героев?
3. КУЛЬМИНАЦИЯ: Опиши самый напряженный момент, переломную точку сюжета.
4. ГЛАВНЫЕ ГЕРОИ: Перечисли имена главных героев и кратко опиши их роли.
5. ВЫВОД: Что автор хотел сказать читателям? Какое послание заложено в книге?

ЕСЛИ КНИГА НЕХУДОЖЕСТВЕННАЯ:
1. ОСНОВНАЯ ТЕМА: Какова главная тема или предмет книги? Какую область освещает?
2. КЛЮЧЕВЫЕ ИДЕИ: Какие основные концепции, теории или идеи предлагает автор?
3. ЦЕЛЕВАЯ АУДИТОРИЯ: Для кого предназначена эта книга?
4. ПРАКТИЧЕСКАЯ ЦЕННОСТЬ: Какую пользу можно извлечь? Какие навыки или знания дает?
5. ВЫВОД: Какова главная цель автора? Почему эту книгу стоит прочитать?

ВАЖНО: Начни ответ с указания типа книги в формате '🎭Книга художественная' или '📄 Книга нехудожественная'.
Затем четко по пунктам дай анализ. Никаких лишних комментариев."""

        try:
            # запрос к Mistral
            response = requests.post(
                self.mistral_url,
                headers={
                    "Authorization": f"Bearer {self.mistral_api_key}",
                    "Content-Type": "application/json; charset=utf-8"
                },
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=30
            )

            # проверяем ответ
            if response.status_code != 200:
                return f"Ошибка API: {response.status_code}"

            result = response.json()

            if 'choices' not in result or len(result['choices']) == 0:
                return "Неожиданный формат ответа от API"

            analysis = result['choices'][0]['message']['content']

            return analysis

        except requests.exceptions.Timeout:
            return "Превышено время ожидания ответа от API"
        except Exception as e:
            return f"Ошибка при анализе: {type(e).__name__}: {e}"
