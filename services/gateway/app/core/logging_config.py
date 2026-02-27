import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter( 
        "%(asctime)s %(levelname)s %(name)s %(message)s" 
        ))

    logging.root.setLevel(logging.INFO) 
    logging.root.addHandler(handler)
    
