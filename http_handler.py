import aiohttp
import asyncio
import json
from datetime import datetime

class Http:
    def __init__(self, log_file="http_error_log.txt"):
        self.log_file = log_file

    async def get(self, url):
        """
        Sends an asynchronous HTTP GET request to a given URL.

        :param url: The URL to send the request to.
        :return: The response as a dictionary.
        :raises: Exception if the request fails or returns an invalid response.
        """
        self.validate_url(url)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            self.log_error(f"GET request failed for URL {url}: {str(e)}")
            raise Exception(f"GET request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON response for GET request to {url}: {str(e)}")
            raise Exception(f"Invalid JSON response: {str(e)}")

    async def put(self, url, data):
        """
        Sends an asynchronous HTTP PUT request to a given URL with a JSON payload.

        :param url: The URL to send the request to.
        :param data: The data to send as JSON.
        :return: The response as a dictionary.
        :raises: Exception if the request fails or returns an invalid response.
        """
        self.validate_url(url)
        self.validate_payload(data)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            self.log_error(f"PUT request failed for URL {url}: {str(e)}")
            raise Exception(f"PUT request failed: {str(e)}")
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON response for PUT request to {url}: {str(e)}")
            raise Exception(f"Invalid JSON response: {str(e)}")

    def validate_url(self, url):
        """
        Validates the URL.

        :param url: The URL to validate.
        :raises: Exception if the URL is invalid.
        """
        if not url.startswith("http://") and not url.startswith("https://"):
            self.log_error(f"Invalid URL: {url}")
            raise Exception(f"Invalid URL: {url}")

    def validate_payload(self, data):
        """
        Validates the payload for a PUT request.

        :param data: The data to validate.
        :raises: Exception if the payload is not a dictionary or is empty.
        """
        if not isinstance(data, dict) or not data:
            self.log_error(f"Invalid payload for PUT request: {data}")
            raise Exception("Invalid payload: Data must be a non-empty dictionary.")

    def log_error(self, message):
        """
        Logs an error message to a file.

        :param message: The error message to log.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as log:
            log.write(f"[{timestamp}] {message}\n")