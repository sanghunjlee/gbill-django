from . import APP_NAME, VERSION
from .view import init_app

if __name__ == "__main__":
    init_app(APP_NAME, VERSION)