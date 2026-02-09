"""Модуль для проверки доменов через WHOIS"""

import socket
import re
from typing import Dict, Optional
from datetime import datetime
import time
import config


class WhoisChecker:
    """Проверка доступности доменов .uz через WHOIS"""
    
    def __init__(self):
        self.server = config.WHOIS_SERVER
        self.port = config.WHOIS_PORT
        self.timeout = config.WHOIS_TIMEOUT
    
    def query_whois(self, domain: str) -> str:
        """
        Прямой WHOIS-запрос к серверу whois.cctld.uz
        
        Args:
            domain: Доменное имя для проверки
            
        Returns:
            Ответ WHOIS-сервера
        """
        try:
            # Создаем сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Подключаемся к WHOIS-серверу
            sock.connect((self.server, self.port))
            
            # Отправляем запрос (домен + перевод строки)
            query = f"{domain}\r\n"
            sock.send(query.encode('utf-8'))
            
            # Получаем ответ
            response = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            
            # Декодируем ответ
            return response.decode('utf-8', errors='ignore')
            
        except socket.timeout:
            return "ERROR: Timeout"
        except socket.gaierror:
            return "ERROR: Cannot resolve WHOIS server"
        except ConnectionRefusedError:
            return "ERROR: Connection refused"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def parse_whois_response(self, response: str, domain: str) -> Dict[str, Optional[str]]:
        """
        Парсинг ответа WHOIS-сервера
        
        Args:
            response: Ответ от WHOIS-сервера
            domain: Проверяемый домен
            
        Returns:
            Словарь с данными: {status, expiry_date, registrar, created_date}
        """
        result = {
            'domain': domain,
            'status': 'Unknown',
            'expiry_date': None,
            'registrar': None,
            'created_date': None,
            'raw_response': response[:500]  # Первые 500 символов для отладки
        }
        
        # Проверяем на ошибки
        if response.startswith('ERROR:'):
            result['status'] = 'Error'
            return result
        
        response_lower = response.lower()
        
        # Проверка: домен не найден / свободен
        not_found_patterns = [
            'not found',
            'no entries found',
            'no match',
            'nothing found',
            'domain not found',
            'not registered'
        ]
        
        if any(pattern in response_lower for pattern in not_found_patterns):
            result['status'] = 'Available'
            return result
        
        # Домен зарегистрирован
        result['status'] = 'Registered'
        
        # Извлекаем дату истечения
        expiry_patterns = [
            r'expir[ey]\s*date:?\s*(\d{4}-\d{2}-\d{2})',
            r'expiration\s*date:?\s*(\d{4}-\d{2}-\d{2})',
            r'expire[sd]?:?\s*(\d{4}-\d{2}-\d{2})',
            r'registry expiry date:?\s*(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in expiry_patterns:
            match = re.search(pattern, response_lower)
            if match:
                result['expiry_date'] = match.group(1)
                break
        
        # Извлекаем дату создания
        created_patterns = [
            r'creation\s*date:?\s*(\d{4}-\d{2}-\d{2})',
            r'created:?\s*(\d{4}-\d{2}-\d{2})',
            r'registered:?\s*(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in created_patterns:
            match = re.search(pattern, response_lower)
            if match:
                result['created_date'] = match.group(1)
                break
        
        # Извлекаем регистратора
        registrar_patterns = [
            r'registrar:?\s*(.+)',
            r'sponsoring registrar:?\s*(.+)',
        ]
        
        for pattern in registrar_patterns:
            match = re.search(pattern, response_lower)
            if match:
                result['registrar'] = match.group(1).strip()
                break
        
        return result
    
    def check_domain(self, username: str) -> Dict[str, Optional[str]]:
        """
        Проверка домена username.uz
        
        Args:
            username: Юзернейм для проверки
            
        Returns:
            Результат проверки WHOIS
        """
        domain = f"{username}.uz"
        
        print(f"  Проверка: {domain}")
        
        # Делаем WHOIS-запрос
        response = self.query_whois(domain)
        
        # Парсим ответ
        result = self.parse_whois_response(response, domain)
        
        # Небольшая задержка между запросами
        time.sleep(0.5)
        
        return result
    
    def check_multiple_domains(self, usernames: list) -> list:
        """
        Проверка нескольких доменов
        
        Args:
            usernames: Список юзернеймов
            
        Returns:
            Список результатов проверки
        """
        results = []
        total = len(usernames)
        
        print(f"\n🔍 Проверка {total} доменов через WHOIS...")
        
        for idx, username in enumerate(usernames, 1):
            print(f"[{idx}/{total}] ", end='')
            result = self.check_domain(username)
            results.append(result)
        
        return results
