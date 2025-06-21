import os
from pathlib import Path

def load_dotenv():
    """Загружает переменные окружения из .env файла"""
    env_path = Path('.') / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("Переменные окружения загружены из .env")
    else:
        print("Файл .env не найден")
