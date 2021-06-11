import logging


logger = logging.getLogger('translation_tower')


def logger_default_policy(my_logger, file="log.log"):

    # Formatter
    log_formatter = logging.Formatter("%(asctime)s  [%(levelname)-5.5s]  %(message)s")

    # Level
    my_logger.setLevel(logging.NOTSET)

    # File handler
    file_handler = logging.FileHandler(file)
    file_handler.setFormatter(log_formatter)
    my_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    my_logger.addHandler(console_handler)

    # Silence some loggers
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("openapi_spec_validator").setLevel(logging.WARNING)
    logging.getLogger("aiohttp_middlewares.cors").setLevel(logging.WARNING)
    logging.getLogger("aiohttp_retry").setLevel(logging.ERROR)