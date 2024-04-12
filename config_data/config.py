from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    RAPID_API_KEY: str

    class Config:
        env_file = '.env'
        case_sensitive = False


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

try:
    setting = Settings().dict()
except ValueError:
    exit("Отсутствуют данные конфигурации в файле .env")

BOT_TOKEN = setting["BOT_TOKEN"]
RAPID_API_KEY = setting["RAPID_API_KEY"]
DEFAULT_COMMANDS = (
    ("lowprice", "Вывести отели по минимальной цене"),
    ("highprice", "Вывести отели по максимальной цене"),
    ("bestdeal", "Вывести отели по расстоянию от центра"),
    ("history", "Вывести историю поиска"))
