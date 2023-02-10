from . import APP_NAME, VERSION, init_app

def main():
    init_app(APP_NAME, VERSION)

if __name__ == '__main__':
    main()