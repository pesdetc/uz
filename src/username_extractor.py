"""Модуль для извлечения юзернеймов из URL"""

import re
from typing import List, Dict, Set
from urllib.parse import urlparse


class UsernameExtractor:
    """Извлечение и фильтрация юзернеймов, заканчивающихся на 'uz'"""
    
    @staticmethod
    def extract_from_url(url: str, source: str) -> str:
        """
        Извлечение юзернейма из URL
        
        Args:
            url: URL профиля
            source: Источник (telegram или instagram)
            
        Returns:
            Юзернейм или пустая строка
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if source == 'telegram':
                # t.me/username или t.me/s/username (для каналов)
                if path.startswith('s/'):
                    username = path.split('/', 1)[1] if '/' in path else ''
                else:
                    username = path.split('/')[0]
                    
            elif source == 'instagram':
                # instagram.com/username или instagram.com/username/
                username = path.split('/')[0]
            else:
                username = ''
            
            # Очистка от параметров
            username = username.split('?')[0].strip()
            
            return username
            
        except Exception as e:
            print(f"  Ошибка при извлечении из {url}: {e}")
            return ''
    
    @staticmethod
    def filter_uz_usernames(username: str) -> bool:
        """
        Проверка, заканчивается ли юзернейм на 'uz'
        
        Args:
            username: Юзернейм для проверки
            
        Returns:
            True если заканчивается на 'uz'
        """
        if not username:
            return False
        
        # Приводим к нижнему регистру для проверки
        username_lower = username.lower()
        
        # Проверяем окончание на 'uz'
        # Допустимы варианты: nameuz, name_uz, name.uz, name-uz
        pattern = r'uz$'
        
        return bool(re.search(pattern, username_lower))
    
    @staticmethod
    def clean_username(username: str) -> str:
        """
        Очистка юзернейма от недопустимых символов
        
        Args:
            username: Исходный юзернейм
            
        Returns:
            Очищенный юзернейм
        """
        # Удаляем символы, недопустимые в доменах
        # Оставляем только буквы, цифры, дефис и подчеркивание
        cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', username)
        return cleaned.lower()
    
    def process_urls(self, urls_dict: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """
        Обработка всех URL и извлечение юзернеймов
        
        Args:
            urls_dict: Словарь с URL по источникам
            
        Returns:
            Список словарей с данными: {source, username, original_username, url}
        """
        results = []
        seen_usernames: Set[str] = set()
        
        for source, urls in urls_dict.items():
            print(f"\n📋 Обработка {source}...")
            
            for url in urls:
                username = self.extract_from_url(url, source)
                
                if username and self.filter_uz_usernames(username):
                    # Проверяем дубликаты
                    username_key = f"{source}:{username.lower()}"
                    
                    if username_key not in seen_usernames:
                        seen_usernames.add(username_key)
                        
                        results.append({
                            'source': source.capitalize(),
                            'username': username,
                            'original_username': username,
                            'url': url
                        })
            
            print(f"  Найдено уникальных uz-юзернеймов: {len([r for r in results if r['source'] == source.capitalize()])}")
        
        return results
