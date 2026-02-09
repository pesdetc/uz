Отлично! Продолжаю:

📄 3. .gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# Results
results/
*.xlsx
*.xls

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
📄 4. main.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Парсер uz-доменов из Telegram и Instagram"""

import sys
from src.google_search import GoogleSearcher
from src.username_extractor import UsernameExtractor
from src.whois_checker import WhoisChecker
from src.excel_exporter import ExcelExporter


def print_banner():
    """Вывод баннера программы"""
    print("=" * 60)
    print(" " * 15 + "Парсер uz-доменов")
    print(" " * 10 + "Telegram & Instagram -> .uz domains")
    print("=" * 60)


def main():
    """Главная функция"""
    print_banner()
    
    try:
        # Шаг 1: Поиск профилей через Google
        print("\n" + "=" * 60)
        print("ЭТАП 1: Поиск профилей через Google")
        print("=" * 60)
        
        searcher = GoogleSearcher()
        urls_dict = searcher.search_all_sources()
        
        total_urls = sum(len(urls) for urls in urls_dict.values())
        print(f"\nВсего найдено URL: {total_urls}")
        
        if total_urls == 0:
            print("Не найдено ни одного URL. Завершение работы.")
            return
        
        # Шаг 2: Извлечение юзернеймов
        print("\n" + "=" * 60)
        print("ЭТАП 2: Извлечение uz-юзернеймов")
        print("=" * 60)
        
        extractor = UsernameExtractor()
        usernames_data = extractor.process_urls(urls_dict)
        
        print(f"\nВсего uz-юзернеймов: {len(usernames_data)}")
        
        if len(usernames_data) == 0:
            print("Не найдено юзернеймов, заканчивающихся на 'uz'. Завершение работы.")
            return
        
        # Шаг 3: Проверка доменов через WHOIS
        print("\n" + "=" * 60)
        print("ЭТАП 3: Проверка доменов через WHOIS")
        print("=" * 60)
        
        checker = WhoisChecker()
        usernames_list = [item['username'] for item in usernames_data]
        whois_results = checker.check_multiple_domains(usernames_list)
        
        # Подсчет статистики
        available = len([r for r in whois_results if r['status'] == 'Available'])
        registered = len([r for r in whois_results if r['status'] == 'Registered'])
        
        print(f"\nПроверка завершена:")
        print(f"   Свободных доменов: {available}")
        print(f"   Занятых доменов: {registered}")
        
        # Шаг 4: Экспорт в Excel
        print("\n" + "=" * 60)
        print("ЭТАП 4: Экспорт результатов")
        print("=" * 60)
        
        exporter = ExcelExporter()
        output_file = exporter.export(usernames_data, whois_results)
        
        print("\n" + "=" * 60)
        print("ГОТОВО!")
        print("=" * 60)
        print(f"\nОтчет доступен: {output_file}")
        print("\nОткройте файл в Excel для просмотра результатов.")
        
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
