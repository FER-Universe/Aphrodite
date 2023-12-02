import json
import os
from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_SECRET_DIR = os.path.join(BASE_DIR, ".config_secret")
    CONFIG_SECRET_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, "setting_local.json")
    CONFIG_HEADER_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, "setting_header.json")

    config_secret_common = json.loads(open(CONFIG_SECRET_COMMON_FILE).read())
    config_header_common = json.loads(open(CONFIG_HEADER_COMMON_FILE).read())

    OPENAI_API_KEY: str = config_secret_common["openai_api_key"]
    OPENAI_HEADERS: str = config_header_common["openai_headers"]

    DB_ID: str = config_secret_common["db_id"]
    DB_PW: str = config_secret_common["db_password"]
    DB_ADDRESS: str = config_secret_common["db_address"]
    DB_NAME: str = config_secret_common["db_name"]

    IP_ADDRESS: str = config_secret_common["ip_address"]
    PORT: str = config_secret_common["port"]
    BASIC_API: str = config_secret_common["basic_api"]
    ADVANCED_API: str = config_secret_common["advanced_api"]


settings = Settings()
