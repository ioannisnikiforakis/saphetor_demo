"""
Basic Logger for the VcfApi app
"""
import logging
import traceback

vcfapi_logger = logging.getLogger()
logging.basicConfig(format='[VCFAPI] %(asctime)s %(message)s')
vcfapi_logger.setLevel(logging.INFO)

def info(message):
    """
    Log an INFO level message
    """
    return vcfapi_logger.info(f"[INFO] {message}")

def debug(message):
    """
    Log a DEBUG level message
    """
    return vcfapi_logger.debug(f"[DEBUG] {message}")

def error(message):
    """
    Log an ERROR level message
    """
    return vcfapi_logger.error(f"[ERROR] {message}")

def logException(err):
    """
    Log an Exception message
    
    Args:
        err(Exception): The exception that we will extract the message from
    """
    err_msg = str(getattr(err, 'message', repr(err)))
    err_trace = ""
    if err.__traceback__:
        err_trace = ''.join(traceback.format_tb(err.__traceback__))
    vcfapi_logger.error(" [*ERROR*] : " + err_msg + "\n" + err_trace)
