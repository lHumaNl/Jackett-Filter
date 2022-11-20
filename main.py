import argparse
import os
from http.server import HTTPServer

from common.http_get_handler import HttpGetHandler
from common.logger_model import LoggerModel
from common.settings import Settings
from models.param_names import ParamNames


def parse_console_args_and_get_settings():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(f"--{ParamNames.UTIL_PORT}", type=int,
                             default=os.environ.get(f"{ParamNames.UTIL_PORT.upper()}", default=9118))

    args_parser.add_argument(f"--{ParamNames.CONFIG_FILE}", type=str,
                             default=os.environ.get(f"{ParamNames.CONFIG_FILE.upper()}", default="config.json"))

    args_dict = args_parser.parse_args().__dict__

    return args_dict


def main():
    LoggerModel.init_logger()

    args_dict = parse_console_args_and_get_settings()
    settings = Settings(args_dict)

    http_get_handler = HttpGetHandler
    http_get_handler.settings = settings

    web_server = HTTPServer(("", settings.util_port), http_get_handler)

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()


if __name__ == '__main__':
    main()
