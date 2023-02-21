import logging


logger = logging.Logger(name="APP", level=logging.DEBUG)

formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
