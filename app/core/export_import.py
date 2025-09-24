"""
Модуль для экспорта и импорта данных портфеля
Поддерживает CSV и JSON форматы
"""

import csv
import json
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.services import list_transactions, get_portfolio_stats, get_sources_with_frequency, get_price_alerts
from app.core.models import TransactionIn, PriceAlertIn
from sqlmodel import Session
from app.storage.db import engine
from app.core.models import Transaction, PriceAlert, SourceMeta


def export_transactions_csv() -> str:
    """Экспорт транзакций в CSV формат"""
    transactions = list_transactions()
    
    if not transactions:
        return ""
    
    # Создаем CSV в памяти
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    headers = [
        'ID', 'Монета', 'Количество', 'Цена', 'Источник', 
        'Тип', 'Дата', 'Заметки', 'Создано'
    ]
    writer.writerow(headers)
    
    # Данные
    for tx in transactions:
        writer.writerow([
            tx.get('id', ''),
            tx.get('coin', ''),
            tx.get('quantity', ''),  # Исправлено: было 'qty'
            tx.get('price', ''),
            tx.get('source', ''),
            tx.get('type', ''),
            tx.get('created_at', ''),
            tx.get('notes', ''),
            tx.get('created_at', '')
        ])
    
    return output.getvalue()


def export_portfolio_json() -> Dict[str, Any]:
    """Экспорт полного портфеля в JSON формат"""
    # Получаем алерты и преобразуем их в словари
    alerts = get_price_alerts()
    alerts_dict = []
    for alert in alerts:
        if hasattr(alert, '__dict__'):
            # Если это объект SQLModel, преобразуем в словарь
            alert_dict = {}
            for key, value in alert.__dict__.items():
                if not key.startswith('_'):
                    # Преобразуем datetime в строку
                    if hasattr(value, 'isoformat'):
                        alert_dict[key] = value.isoformat()
                    else:
                        alert_dict[key] = value
            alerts_dict.append(alert_dict)
        else:
            # Если это уже словарь
            alerts_dict.append(alert)
    
    return {
        'export_info': {
            'version': '1.8.0',
            'export_date': datetime.now().isoformat(),
            'description': 'Полный бэкап портфеля Crypto Portfolio Manager'
        },
        'transactions': list_transactions(),
        'portfolio_stats': get_portfolio_stats(),
        'sources': get_sources_with_frequency(),
        'price_alerts': alerts_dict,
        'metadata': {
            'total_transactions': len(list_transactions()),
            'export_timestamp': datetime.now().timestamp()
        }
    }


def import_transactions_csv(csv_content: str) -> Dict[str, Any]:
    """Импорт транзакций из CSV"""
    result = {
        'success': True,
        'imported': 0,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Парсим CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        for row_num, row in enumerate(csv_reader, start=2):  # Начинаем с 2 (пропускаем заголовок)
            try:
                # Валидация и преобразование данных
                transaction_data = {
                    'coin': row.get('Монета', '').strip(),
                    'qty': float(row.get('Количество', 0)) if row.get('Количество') else 0.0,
                    'price': float(row.get('Цена', 0)) if row.get('Цена') else 0.0,
                    'source': row.get('Источник', '').strip(),
                    'type': row.get('Тип', 'buy').strip().lower(),
                    'notes': row.get('Заметки', '').strip()
                }
                
                # Валидация обязательных полей
                if not transaction_data['coin']:
                    result['errors'].append(f"Строка {row_num}: Отсутствует название монеты")
                    continue
                
                if transaction_data['qty'] <= 0:
                    result['errors'].append(f"Строка {row_num}: Некорректное количество")
                    continue
                
                if transaction_data['price'] <= 0:
                    result['errors'].append(f"Строка {row_num}: Некорректная цена")
                    continue
                
                # Добавляем транзакцию
                from app.core.services import add_transaction
                transaction_id = add_transaction(TransactionIn(**transaction_data))
                result['imported'] += 1
                
            except ValueError as e:
                result['errors'].append(f"Строка {row_num}: Ошибка преобразования данных - {str(e)}")
            except Exception as e:
                result['errors'].append(f"Строка {row_num}: Неожиданная ошибка - {str(e)}")
        
        if result['errors']:
            result['success'] = False
            
    except Exception as e:
        result['success'] = False
        result['errors'].append(f"Ошибка чтения CSV: {str(e)}")
    
    return result


def import_portfolio_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Импорт полного портфеля из JSON"""
    result = {
        'success': True,
        'imported_transactions': 0,
        'imported_alerts': 0,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Проверяем версию
        export_info = json_data.get('export_info', {})
        if export_info.get('version') != '1.7.0':
            result['warnings'].append(f"Версия файла {export_info.get('version', 'неизвестна')} может быть несовместима с текущей версией 1.7.0")
        
        # Импорт транзакций
        transactions = json_data.get('transactions', [])
        for tx_data in transactions:
            try:
                # Преобразуем в формат TransactionIn
                transaction_input = TransactionIn(
                    coin=tx_data.get('coin', ''),
                    qty=float(tx_data.get('qty', 0)),
                    price=float(tx_data.get('price', 0)),
                    source=tx_data.get('source', ''),
                    type=tx_data.get('type', 'buy'),
                    notes=tx_data.get('notes', '')
                )
                
                from app.core.services import add_transaction
                add_transaction(transaction_input)
                result['imported_transactions'] += 1
                
            except Exception as e:
                result['errors'].append(f"Ошибка импорта транзакции: {str(e)}")
        
        # Импорт алертов
        alerts = json_data.get('price_alerts', [])
        for alert_data in alerts:
            try:
                alert_input = PriceAlertIn(
                    coin=alert_data.get('coin', ''),
                    target_price=float(alert_data.get('target_price', 0)),
                    alert_type=alert_data.get('alert_type', 'above'),
                    notes=alert_data.get('notes', '')
                )
                
                from app.core.services import add_price_alert
                add_price_alert(alert_input)
                result['imported_alerts'] += 1
                
            except Exception as e:
                result['errors'].append(f"Ошибка импорта алерта: {str(e)}")
        
        if result['errors']:
            result['success'] = False
            
    except Exception as e:
        result['success'] = False
        result['errors'].append(f"Ошибка импорта JSON: {str(e)}")
    
    return result


def get_export_statistics() -> Dict[str, Any]:
    """Получить статистику для экспорта"""
    transactions = list_transactions()
    stats = get_portfolio_stats()
    
    return {
        'total_transactions': len(transactions),
        'total_value': stats.get('total_value', 0),
        'portfolio_coins': len(stats.get('positions', [])),
        'active_alerts': len(get_price_alerts()),
        'sources_count': len(get_sources_with_frequency()),
        'last_export': datetime.now().isoformat()
    }


def validate_csv_format(csv_content: str) -> Dict[str, Any]:
    """Валидация формата CSV перед импортом"""
    result = {
        'valid': True,
        'rows_count': 0,
        'headers': [],
        'errors': []
    }
    
    try:
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        result['headers'] = csv_reader.fieldnames or []
        
        # Проверяем обязательные заголовки
        required_headers = ['Монета', 'Количество', 'Цена']
        missing_headers = [h for h in required_headers if h not in result['headers']]
        
        if missing_headers:
            result['valid'] = False
            result['errors'].append(f"Отсутствуют обязательные заголовки: {', '.join(missing_headers)}")
        
        # Подсчитываем строки
        result['rows_count'] = sum(1 for _ in csv_reader)
        
        if result['rows_count'] == 0:
            result['errors'].append("CSV файл не содержит данных")
            result['valid'] = False
            
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Ошибка чтения CSV: {str(e)}")
    
    return result
