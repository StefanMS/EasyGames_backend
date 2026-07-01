import logging

logging.basicConfig(level=logging.INFO, filename="app/logs/backend.log",
                    filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")