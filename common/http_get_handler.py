import json
import logging
import os
import traceback
from http.server import BaseHTTPRequestHandler
from typing import Optional

import requests
from requests import Response

from common.settings import Settings
from models.jackett_response_keys import JackettResponseKeys


class HttpGetHandler(BaseHTTPRequestHandler):
    settings: Settings
    __response_message: str
    __is_ok = True

    def do_OPTIONS(self):
        self.send_response(204)

        self.send_header("Allow", "OPTIONS, GET")
        self.end_headers()

    def do_GET(self):
        jackett_response = self.__get_jackett_response()

        if jackett_response is not None:
            try:
                self.__response_message = json.dumps(self.__filter_results(jackett_response.json()), ensure_ascii=True)
            except Exception:
                self.__is_ok = False
                self.__response_message = '{"Error": "Failed to filtering response from Jackett"}'
                logging.error(f"Failed to filtering response from Jackett{os.linesep + traceback.format_exc()}")

        if self.__is_ok:
            self.send_response(200)
        else:
            self.send_response(500)

        self.__add_headers_for_response()

        self.wfile.write(self.__response_message.encode())

    @staticmethod
    def __calculate_film_size_in_gibibyte(film_size_in_bytes) -> float:
        gibibyte_film_size = round(film_size_in_bytes / (1024 * 1024 * 1024), 2)

        return gibibyte_film_size

    def __filter_results(self, jackett_response: dict) -> dict:
        valid_results = []
        valid_indexers = jackett_response[JackettResponseKeys.INDEXERS]

        for i in range(len(valid_indexers)):
            valid_indexers[i][JackettResponseKeys.RESULTS] = 0

        for film_dict in jackett_response[JackettResponseKeys.RESULTS]:
            if film_dict[JackettResponseKeys.SEEDERS] >= self.settings.min_seeds:

                gibibyte_film_size = HttpGetHandler.__calculate_film_size_in_gibibyte(
                    film_dict[JackettResponseKeys.SIZE])

                if self.settings.max_size_of_torrent is not None and self.settings.min_size_of_torrent is not None:
                    if self.settings.min_size_of_torrent <= gibibyte_film_size <= self.settings.max_size_of_torrent:
                        valid_results.append(film_dict)
                    else:
                        continue

                elif self.settings.max_size_of_torrent is not None:
                    if gibibyte_film_size <= self.settings.max_size_of_torrent:
                        valid_results.append(film_dict)
                    else:
                        continue
                elif self.settings.min_size_of_torrent is not None:
                    if gibibyte_film_size >= self.settings.min_size_of_torrent:
                        valid_results.append(film_dict)
                    else:
                        continue
                else:
                    valid_results.append(film_dict)

                valid_indexers = self.__increment_index_result_count(valid_indexers,
                                                                     film_dict[JackettResponseKeys.TRACKERID])

        return {JackettResponseKeys.RESULTS: valid_results,
                JackettResponseKeys.INDEXERS: valid_indexers}

    def __add_headers_for_response(self):
        headers_dict = {
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-store,no-cache",
            "Content-Type": "application/json; charset=utf-8",
            "Pragma": "no-cache",
            "Vary": "Accept-Encoding",
        }

        for header_key, header_value in headers_dict.items():
            self.send_header(header_key, header_value)

        self.end_headers()

    @staticmethod
    def __increment_index_result_count(valid_indexers: list, tracker_id: str) -> list:
        for i in range(len(valid_indexers)):
            if valid_indexers[i][JackettResponseKeys.ID] == tracker_id:
                valid_indexers[i][JackettResponseKeys.RESULTS] += 1

        return valid_indexers

    def __get_jackett_response(self) -> Optional[Response]:
        try:
            jackett_response = requests.get(f"{self.settings.jackett_host}{self.path}")
        except Exception:
            logging.error(f"Failed to send request to Jackett{os.linesep + traceback.format_exc()}")
            self.__response_message = '{"Error": "Failed to send request to Jackett"}'
            jackett_response = None
            self.__is_ok = False

        return jackett_response
