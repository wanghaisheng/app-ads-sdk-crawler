import logging
import os
import pathlib
import sys
import tomllib
import typing
from logging import Formatter
from logging.handlers import RotatingFileHandler

HOME = pathlib.Path.home()
PROJECT_NAME = "adscrawler"
TOP_CONFIGDIR = pathlib.Path(HOME, pathlib.Path(".config"))
CONFIG_DIR = pathlib.Path(TOP_CONFIGDIR, pathlib.Path(PROJECT_NAME))
LOG_DIR = pathlib.Path(CONFIG_DIR, pathlib.Path("logs"))
MODULE_DIR = pathlib.Path(__file__).resolve().parent
PACKAGE_DIR = pathlib.Path(__file__).resolve().parent.parent

# APK File dirs
APKS_FILES_DIR = pathlib.Path(HOME, "apk-files")
APKS_DIR = pathlib.Path(APKS_FILES_DIR, "apks")
XAPKS_DIR = pathlib.Path(APKS_FILES_DIR, "xapks")
APK_PARTIALS_DIR = pathlib.Path(APKS_FILES_DIR, "apk-partials")
APK_UNZIPPED_DIR = pathlib.Path(APKS_FILES_DIR, "tmp-unzipped")
ANDROID_SDK = pathlib.Path(HOME, "Android/Sdk/build-tools/35.0.0")


@typing.no_type_check
def handle_exception(exc_type, exc_value, exc_traceback) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def check_config_dirs() -> None:
    dirs = [TOP_CONFIGDIR, CONFIG_DIR, LOG_DIR]
    for _dir in dirs:
        if not pathlib.Path.exists(_dir):
            pathlib.Path.mkdir(_dir, exist_ok=True)


FORMATTER = Formatter(
    "%(asctime)s.%(msecs)03d | "
    "%(process)d | "
    "%(levelname)-5s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)


FORMATTER.datefmt = "%Y-%m-%d %H:%M:%S"


def get_logger(mod_name: str, sep_file: str | None = "main") -> logging.Logger:
    check_config_dirs()

    # Get or create logger
    logger = logging.getLogger(mod_name)

    # Clear any existing handlers
    logger.handlers.clear()

    # Set level
    logger.setLevel(logging.INFO)

    # Add file handler for individual log file
    indiv_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, f"{sep_file}.log"),
        maxBytes=50 * 1024 * 1024,
        backupCount=10,
    )
    indiv_handler.setFormatter(FORMATTER)
    logger.addHandler(indiv_handler)

    if sep_file != "main":
        root_logger = logging.getLogger(PROJECT_NAME)
        if not root_logger.handlers:
            # Add main file handler if it doesn't exist
            main_handler = RotatingFileHandler(
                filename=os.path.join(LOG_DIR, "main.log"),
                maxBytes=50 * 1024 * 1024,
                backupCount=10,
            )
            main_handler.setFormatter(FORMATTER)
            root_logger.addHandler(main_handler)

            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(FORMATTER)
            root_logger.addHandler(console_handler)

        # Ensure the root logger level is set to capture all messages
        root_logger.setLevel(logging.INFO)

        # Set propagate to True for non-main loggers
        logger.propagate = True
    else:
        # For the main logger (root logger), add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(FORMATTER)
        logger.addHandler(console_handler)
        logger.propagate = False  # Main logger shouldn't propagate

    return logger


# Set global handling of uncaught exceptions
sys.excepthook = handle_exception

logger = get_logger(__name__)


CONFIG_FILENAME = "config.toml"

CONFIG_FILE_PATH = pathlib.Path(CONFIG_DIR, CONFIG_FILENAME)
if not pathlib.Path.exists(CONFIG_FILE_PATH):
    error = f"Couldn't find {CONFIG_FILENAME} please add to {CONFIG_DIR}"
    logger.error(error)
    raise FileNotFoundError(error)


with open(CONFIG_FILE_PATH, "rb") as f:
    CONFIG = tomllib.load(f)


DATE_FORMAT = "%Y-%m-%d"


logger.info("Logger and Config loaded")


DEVLEOPER_IGNORE_TLDS = [
    "00webhostapp.com",
    "bitballoon.com",
    "blogger.com",
    "linkedin.com",
    "blogspot.com",
    "blogspot.co.id",
    "blogspot.in",
    "bytehost6.com",
    "facebook.com",
    "flycricket.io",
    "github.io",
    "github.com",
    "instagram.com",
    "netlify.com",
    "page.link",
    "site123.me",
    "simplesite.com",
    "subsplash.com",
    "twitter.com",
    "tumblr.com",
    "weebly.com",
    "wix.com",
    "wixsite.com",
    "wordpress.com",
    "youtube.com",
]
