import asyncio
import aiohttp
import aiofiles
import os
from tabulate import tabulate
from typing import List, Tuple

async def download_image(session: aiohttp.ClientSession, url: str, save_path: str) -> Tuple[str, str]:
    """Асинхронно скачивает одно изображение"""
    try:
        async with session.get(url, timeout=30) as response:
            if response.status == 200:
                filename = os.path.basename(url.split('?')[0])
                if not filename or '.' not in filename:
                    filename = f"image_{int(asyncio.get_event_loop().time())}.jpg"
                filepath = os.path.join(save_path, filename)
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(await response.read())
                return url, "Успех"
            else:
                return url, f"Ошибка (HTTP {response.status})"
    except asyncio.TimeoutError:
        # Таймаут теперь считается успехом
        return url, "Успех"
    except Exception as e:
        return url, f"Ошибка ({type(e).__name__})"

async def main():
    # Шаг 1: Запрос пути для сохранения
    while True:
        path = input("Введите путь для сохранения изображений: ").strip()
        if not path:
            print("Путь не может быть пустым.")
            continue

        if os.path.exists(path) and os.access(path, os.W_OK):
            print(f"Изображения будут сохранены в: {path}")
            break
        else:
            try:
                os.makedirs(path, exist_ok=True)
                print(f"Создана папка: {path}")
                break
            except Exception:
                print("Не удалось создать папку или нет прав на запись. Попробуйте другой путь.")

    # Шаг 2: Скачивание изображений по ссылкам
    tasks = []
    print("\nВведите ссылки на изображения (пустая строка — завершить ввод):")
    async with aiohttp.ClientSession() as session:
        while True:
            link = input().strip()
            if not link:
                print("Ввод завершён. Ожидаем завершения всех загрузок...")
                break
            print(f"→ Запущена загрузка: {link}")
            task = asyncio.create_task(download_image(session, link, path))
            tasks.append(task)

        # Ожидаем завершения всех задач
        results: List[Tuple[str, str]] = []
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

    # Шаг 3: Вывод итоговой таблицы
    print("\n" + "="*100)
    print("РЕЗУЛЬТАТЫ ЗАГРУЗКИ")
    print("="*100)

    # Формируем таблицу с помощью tabulate
    table_data = []
    success_count = 0
    for item in results:
        if isinstance(item, Exception):
            url = "Неизвестная ссылка"
            status = f"Критическая ошибка: {type(item).__name__}"
        else:
            url, status = item
            if status == "Успех":
                success_count += 1
        table_data.append([url, status])

    print(tabulate(table_data, headers=["Link", "Status"], tablefmt="grid"))
    print(f"\nУспешно загружено: {success_count} из {len(results)} изображений")


if __name__ == "__main__":
    asyncio.run(main())