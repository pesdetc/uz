"""Модуль для поиска профилей через Google"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict
import config


class GoogleSearcher:
    """Поиск профилей Telegram и Instagram через Google"""
    
    def __init__(self):
        self.headers = {'User-Agent': config.USER_AGENT}
        self.session = requests.Session()
    
    def search(self, query: str, max_results: int = 50) -> List[str]:
        """
        Поиск по запросу через Google
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных URL
        """
        urls = []
        num_pages = (max_results // 10) + 1  # Google показывает ~10 результатов на страницу
        
        for page in range(num_pages):
            try:
                start = page * 10
                search_url = f"https://www.google.com/search?q={query}&start={start}"
                
                print(f"  Поиск: {query} (страница {page + 1})")
                
                response = self.session.get(search_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Извлекаем ссылки из результатов поиска
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    
                    # Фильтруем ссылки Google
                    if '/url?q=' in href:
                        # Извлекаем реальный URL
                        match = re.search(r'/url\?q=(.*?)&', href)
                        if match:
                            url = match.group(1)
                            if self._is_valid_url(url):
                                urls.append(url)
                
                # Задержка между запросами
                time.sleep(config.REQUEST_DELAY)
                
                if len(urls) >= max_results:
                    break
                    
            except Exception as e:
                print(f"  Ошибка при поиске: {e}")
                continue
        
        return urls[:max_results]
    
    def _is_valid_url(self, url: str) -> bool:
        """Проверка валидности URL"""
        # Проверяем, что это Telegram или Instagram
        return ('t.me/' in url or 'instagram.com/' in url) and url.startswith('http')
    
    def search_all_sources(self) -> Dict[str, List[str]]:
        """
        Поиск по всем источникам (Telegram и Instagram)
        
        Returns:
            Словарь с результатами: {'telegram': [...], 'instagram': [...]}
        """
        results = {}
        
        for source, query in config.SEARCH_QUERIES.items():
            print(f"\n🔍 Поиск {source}...")
            urls = self.search(query, config.MAX_RESULTS_PER_SOURCE)
            results[source] = urls
            print(f"  Найдено: {len(urls)} URL")
        
        return results
