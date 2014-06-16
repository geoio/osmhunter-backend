import subprocess
import logging


APP_NAME = "address-suggestion"

GIT_VERSION =  subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().replace('\n', '')

LOG_LEVEL = logging.DEBUG
LOG_FILE = "stdout.log"


DEBUG = True


BOTTLE = {

    "host": "localhost",
    "port": 8060,
    "debug": DEBUG,
    "reloader": DEBUG
}