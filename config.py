"""Конфигурация парсера uz-доменов"""

# Настройки поиска
SEARCH_QUERIES = {
    'telegram': 'site:t.me *uz',
    'instagram': 'site:instagram.com *uz'
}

# Количество результатов для каждого источника
MAX_RESULTS_PER_SOURCE = 50

# WHOIS сервер для .uz доменов
WHOIS_SERVER = 'whois.cctld.uz'
WHOIS_PORT = 43
WHOIS_TIMEOUT = 10

# Настройки экспорта
OUTPUT_FILENAME = 'uz_domains_report.xlsx'
OUTPUT_DIR = 'results'

# User-Agent для запросов
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Задержка между запросами (секунды)
REQUEST_DELAY = 2
