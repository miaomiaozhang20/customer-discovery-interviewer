import logging 
from io import StringIO 
from typing import Tuple 

def setup_logger(name:str) -> Tuple[StringIO, logging.Logger]:
    """Sets up a logger object with a StringIO handler for Streamlit GUI purposes

    Logs are set up this way to make saving logs to Dropbox easier and more convenient 

    Args:
        name (str): the name of the logger 

    Returns:
        Tuple[StringIO, logging.Logger]: a tuple of the StringIO object where logs are saved to, and the logger object itself 
    """
    # Create StringIO object
    log_stream = StringIO()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatter with your specified format
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d\t%(levelname)s\t%(name)s %(module)s\t%(message)s",
        datefmt="%Y-%m-%d %T"  # %T is equivalent to %H:%M:%S
    )
    
    # Create StreamHandler that writes to StringIO
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return log_stream, logger