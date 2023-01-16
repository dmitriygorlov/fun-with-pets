import logging


class Logger:
    def __init__(self, name, file_name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.file_handler = logging.FileHandler(f"logs/{file_name}")
        self.file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(self.file_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)
