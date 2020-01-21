import time

# log file name
LOG_FNAME = "client.log";

# logger levels
LVL_OFF = 0
LVL_FATAL = 1
LVL_ERROR = 2
LVL_WARNING = 3
LVL_INFO = 4
LVL_DEBUG = 5
LVL_TRACE = 6

# severity message constants
LOG_FATAL = "[FATAL]   "
LOG_ERROR = "[ERROR]   "
LOG_WARNING = "[WARNING] "
LOG_INFO = "[INFO]    "
LOG_DEBUG = "[DEBUG]   "
LOG_TRACE = "[TRACE]   "


def get_time():
    return time.strftime("[%d.%m.%y %H:%M:%S] ")


# clean old log file on new start of program
with open(LOG_FNAME, "w") as _f:
    _f.write(LOG_INFO + get_time() + "Cleaning log file\n")


def fatal(_msg):
    with open(LOG_FNAME, "a") as f:
        msg = LOG_FATAL + get_time() + _msg + "\n"
        f.write(msg)
        print(msg, end="")


def error(_msg):
    with open(LOG_FNAME, "a") as f:
        msg = LOG_ERROR + get_time() + _msg + "\n"
        f.write(msg)
        print(msg, end="")


def warning(_msg):
    with open(LOG_FNAME, "a") as f:
        msg = LOG_WARNING + get_time() + _msg + "\n"
        f.write(msg)
        print(msg, end="")


def info(_msg):
    with open(LOG_FNAME, "a") as f:
        msg = LOG_INFO + get_time() + _msg + "\n"
        f.write(msg)
        print(msg, end="")


def debug(_msg):
    with open(LOG_FNAME, "a") as f:
        msg = LOG_DEBUG + get_time() + _msg + "\n"
        f.write(msg)
        print(msg, end="")


def trace(_msg):
    with open(LOG_FNAME, "a") as f:
        msg = LOG_TRACE + get_time() + _msg + "\n"
        f.write(msg)
        print(msg, end="")
