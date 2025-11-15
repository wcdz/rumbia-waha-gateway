import logging
from pythonjsonlogger import jsonlogger
import src.utils.environment as env
from datetime import datetime
from pytz import timezone

# Configuración básica de tu logger
format_str = '%(message)%(levelname)%(asctime)%(filename)%(lineno)%(funcName)'
formatter = jsonlogger.JsonFormatter(
    format_str, 
    rename_fields={
        "levelname": "level", 
        "asctime": "time", 
        "message": "msg", 
        "funcName": "function_name",
        "filename": "caller",
    }
)
logging.Formatter.converter = lambda *args: datetime.now(tz=timezone('America/Lima')).timetuple()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(env.LOG_LEVEL)
logger.addHandler(handler)