import logging


def find_log_level(message):
    """Attempts to find the log level this message has been logged. Can return -1 if the log level cannot be determined. The found 
    log level can then be used to re-log the message in the orchestrator."""
    
    target = message.lower()
    if target.find('info') > 0: return logging.INFO
    if target.find('debug') > 0: return logging.DEBUG
    if target.find('warn') > 0: return logging.WARNING
    if target.find('error') > 0: return logging.ERROR
    if target.find('trace') > 0: return logging.DEBUG
    return None

def find_with_default(message, default='info'):
    level = find_log_level(message)
    if level is not None: return level
    else: return logging._checkLevel(default.upper())

def relog(logger, message, default='info'):
    level = find_with_default(message, default)
    if level >= 0: logger.log(level, message)
    else: logger.info(message)
