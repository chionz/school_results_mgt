import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Define your JWT secret and algorithm
SECRET_KEY = os.getenv("SECRET_KEY", "MY SECRET KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
templates_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

IS_PRODUCTION = ENVIRONMENT == "production"
DEBUG = not IS_PRODUCTION

LOG_DIR = os.getenv("LOG_DIR", "logs")
