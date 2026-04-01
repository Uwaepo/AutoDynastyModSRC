# Python Modules
import datetime

from pathlib import Path

# My Modules
from .. import constants

def debug_log(msg: str):
    if constants.DEBUG_LOGGING_ENABLED != True:
        return
    try:
        with open(constants.SIMS4_DOCUMENTS_PATH / (f"{datetime.date.today()} [{constants.MOD_AUTHOR}]-{constants.MOD_NAME}.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}\n")
    except Exception:
        pass

def args_to_string(*args, **kwargs):
    parts = []

    for i, arg in enumerate(args):
        parts.append(f"arg{i}={arg} ({type(arg).__name__})")

    for key, value in kwargs.items():
        parts.append(f"{key}={value} ({type(value).__name__})")

    return ", ".join(parts)
