import argparse
import logging
import os
import sys


class Settings:
    util_port: int

    jackett_host: str

    min_seeds: int
    min_size_of_torrent: float
    max_size_of_torrent: float

    def __init__(self, args_dict):
        self.util_port = args_dict["util_port"]

        self.jackett_host = args_dict["jackett_host"]

        self.min_seeds = args_dict["min_seeds"]
        self.min_size_of_torrent = args_dict["min_size_of_torrent"]
        self.max_size_of_torrent = args_dict["max_size_of_torrent"]

        if self.jackett_host is None:
            logging.error("Jacket host is NULL!")
            sys.exit(1)

        if self.min_size_of_torrent is not None and self.max_size_of_torrent is not None:
            if self.min_size_of_torrent >= self.max_size_of_torrent:
                logging.error("Min size of torrent can't be greater then max")
                sys.exit(1)


def parse_console_args_and_get_settings() -> Settings:
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--util_port", type=int, default=os.environ.get("UTIL_PORT", default=9118))

    args_parser.add_argument("--jackett_host", type=str, default=os.environ.get("JACKETT_HOST"))

    args_parser.add_argument("--min_seeds", type=int, default=os.environ.get("MIN_SEEDS", default=2))

    args_parser.add_argument("--min_size_of_torrent", type=float,
                             default=os.environ.get("MIN_SIZE_OF_TORRENT", default=1.0))
    args_parser.add_argument("--max_size_of_torrent", type=float, default=os.environ.get("MAX_SIZE_OF_TORRENT"))

    args_dict = args_parser.parse_args().__dict__

    settings = Settings(args_dict)

    return settings
