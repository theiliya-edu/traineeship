import logging


def setup_logger(service_name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [%(levelname)s] [{service_name.upper()}] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(service_name)
