import json
import logging
import os
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

import requests

from common.settings import Settings


class HttpGetHandler(BaseHTTPRequestHandler):
    settings: Settings
    __response_message: str
    __api_key_from_request: str
    __is_ok = True

    def do_GET(self):
        if self.settings.jackett_api_key is not None:
            self.__replace_api_key_in_path()

        jackett_response = self.__get_jackett_response()

        if jackett_response is not None:
            try:
                self.__response_message = json.dumps(self.__filter_results(jackett_response), ensure_ascii=False)
            except Exception:
                self.__is_ok = False
                self.__response_message = '{"Error": "Failed to filtering response from Jackett"}'
                logging.error(f"Failed to filtering response from Jackett{os.linesep + traceback.format_exc()}")

        if self.__is_ok:
            self.send_response(200)
        else:
            self.send_response(500)

        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store,no-cache")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Pragma", "no-cache")
        self.send_header("Vary", "Accept-Encoding")
        self.end_headers()

        self.wfile.write(self.__response_message.encode())

    def __filter_results(self, jackett_response: dict) -> dict:
        valid_results = []
        valid_indexers = jackett_response["Indexers"]

        for i in range(len(valid_indexers)):
            valid_indexers[i]["Results"] = 0

        for film_dict in jackett_response["Results"]:
            if film_dict["Seeders"] >= self.settings.min_seeds:

                file_size = round(film_dict["Size"] / (1024 * 1024 * 1024), 2)

                if self.settings.max_size_of_torrent is not None and self.settings.min_size_of_torrent is not None:
                    if self.settings.min_size_of_torrent <= file_size <= self.settings.max_size_of_torrent:
                        valid_results.append(film_dict)
                    else:
                        continue

                elif self.settings.max_size_of_torrent is not None:
                    if file_size <= self.settings.max_size_of_torrent:
                        valid_results.append(film_dict)
                    else:
                        continue
                elif self.settings.min_size_of_torrent is not None:
                    if file_size >= self.settings.min_size_of_torrent:
                        valid_results.append(film_dict)
                    else:
                        continue
                else:
                    valid_results.append(film_dict)

                valid_indexers = self.__increment_index_result_count(valid_indexers, film_dict["TrackerId"])

        return {"Results": valid_results,
                "Indexers": valid_indexers}

    @staticmethod
    def __increment_index_result_count(valid_indexers: list, tracker_id: str) -> list:
        for i in range(len(valid_indexers)):
            if valid_indexers[i]["ID"] == tracker_id:
                valid_indexers[i]["Results"] += 1

        return valid_indexers

    def __replace_api_key_in_path(self):
        try:
            parsed_api_query = [api_key_query
                                for api_key_query in urlparse(self.path).query.split("&")
                                if api_key_query.__contains__("apikey")][0]

            self.__api_key_from_request = parsed_api_query.split("=")[1]

            self.path = self.path.replace(parsed_api_query, f"apikey={self.settings.jackett_api_key}")
        except Exception:
            logging.error(f"Failed to parse api key from request{os.linesep + traceback.format_exc()}")
            self.__is_ok = False
            self.__response_message = '{"Error": "Failed to parse api key from request"}'

    def __get_jackett_response(self):
        try:
            jackett_response = requests.get(
                f"{self.settings.jackett_protocol}://{self.settings.jackett_host}{self.path}").json()
        except Exception:
            logging.error(f"Failed to send request to Jackett{os.linesep + traceback.format_exc()}")
            self.__response_message = '{"Error": "Failed to send request to Jackett"}'
            jackett_response = None
            self.__is_ok = False

        return jackett_response
