import os
import logging
from logging.handlers import TimedRotatingFileHandler

class AppLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name, log_dir='logs', log_file='my_app.log'):
        if hasattr(self, 'logger'):
            return
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Asegura que el directorio de logs existe
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configura la ruta completa del archivo de log
        log_path = os.path.join(log_dir, log_file)

        # Crea un manejador de archivos que registra todos los mensajes DEBUG y superiores
        # y que crea un nuevo archivo de log cada día
        fh = TimedRotatingFileHandler(log_path, when='midnight', interval=1, backupCount=7)
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)