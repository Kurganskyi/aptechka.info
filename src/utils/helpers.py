"""
Вспомогательные функции
"""

import re
from typing import Optional
from datetime import datetime, timedelta


def format_price_kopecks(kopecks: int) -> str:
    """Форматирование цены в копейках в BYN"""
    byn = kopecks / 100
    return f"{byn:.2f} BYN"


def validate_telegram_username(username: Optional[str]) -> bool:
    """Валидация Telegram username"""
    if not username:
        return True
    
    # Username должен начинаться с @ и содержать только буквы, цифры и _
    pattern = r'^@[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def format_user_display_name(first_name: Optional[str], last_name: Optional[str], username: Optional[str]) -> str:
    """Форматирование отображаемого имени пользователя"""
    if username:
        return f"@{username}"
    
    parts = [first_name, last_name]
    full_name = " ".join(filter(None, parts))
    
    return full_name or "Неизвестно"


def is_admin_user(telegram_id: int, admin_ids: list[int]) -> bool:
    """Проверка, является ли пользователь администратором"""
    return telegram_id in admin_ids


def generate_referral_link(bot_username: str, user_id: int) -> str:
    """Генерация реферальной ссылки"""
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


def parse_referral_start_param(start_param: str) -> Optional[int]:
    """Парсинг реферального параметра из start команды"""
    if start_param.startswith("ref_"):
        try:
            return int(start_param[4:])
        except ValueError:
            return None
    return None


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """Форматирование даты и времени"""
    return dt.strftime(format_str)


def get_time_until_expiry(expires_at: datetime) -> str:
    """Получить время до истечения в человеко-читаемом формате"""
    now = datetime.utcnow()
    if expires_at <= now:
        return "Истек"
    
    delta = expires_at - now
    
    if delta.days > 0:
        return f"{delta.days} дн. {delta.seconds // 3600} ч."
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours} ч. {minutes} мин."
    else:
        minutes = delta.seconds // 60
        return f"{minutes} мин."


def sanitize_filename(filename: str) -> str:
    """Очистка имени файла от небезопасных символов"""
    # Удаляем небезопасные символы
    safe_chars = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Ограничиваем длину
    return safe_chars[:100]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Обрезка текста с суффиксом"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_phone_number(text: str) -> Optional[str]:
    """Извлечение номера телефона из текста"""
    # Простая регулярка для белорусских номеров
    pattern = r'\+375\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Маскирование чувствительных данных"""
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars)
