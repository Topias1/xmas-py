import os
import asyncio
from dotenv import load_dotenv
from http_handler import Http
from datetime import datetime

class Bridge:
    def __init__(self):
        """
        Bridge constructor.
        Initializes the bridge IP, token, and HTTP handler.
        """
        load_dotenv()
        self.ip = os.getenv('HUE_BRIDGE_LOCAL_IP') if os.getenv('DEV') == 'true' else os.getenv('HUE_BRIDGE_REMOTE_IP')
        self.token = os.getenv('HUE_TOKEN')
        self.http = Http()
        asyncio.run(self.validate_bridge_connection())  # Run the async validation method

    async def validate_bridge_connection(self):
        """
        Validates the connection to the Philips Hue Bridge.
        Raises an exception if the bridge is unreachable or credentials are invalid.
        """
        url = f"http://{self.ip}/api/{self.token}/config"
        try:
            response = await self.http.get(url)  # Await the async HTTP request
            if 'name' not in response:
                self.log_error(f"Invalid response from Hue Bridge: {response}")
                raise Exception("Unable to connect to the Hue Bridge. Check your IP and token.")
        except Exception as e:
            self.log_error(f"Bridge validation failed: {str(e)}")
            raise Exception(f"Bridge validation failed: {str(e)}")

    def get_url(self, light_id):
        """
        Generates the API URL for a specific light.

        :param light_id: The ID of the light.
        :return: The API URL for the light.
        """
        self.validate_light_id(light_id)
        return f"http://{self.ip}/api/{self.token}/lights/{light_id}/state"

    async def turn_on_light(self, light_id):
        """
        Turns on a light.

        :param light_id: The ID of the light.
        :return: The API response as a dictionary.
        """
        try:
            url = self.get_url(light_id)
            data = {"on": True}
            return await self.http.put(url, data)  # Await the async HTTP request
        except Exception as e:
            self.log_error(f"Failed to turn on light {light_id}: {str(e)}")
            raise e

    async def turn_off_light(self, light_id):
        """
        Turns off a light.

        :param light_id: The ID of the light.
        :return: The API response as a dictionary.
        """
        try:
            url = self.get_url(light_id)
            data = {"on": False}
            return await self.http.put(url, data)  # Await the async HTTP request
        except Exception as e:
            self.log_error(f"Failed to turn off light {light_id}: {str(e)}")
            raise e

    async def set_light_color(self, light_id, hue, brightness, saturation):
        """
        Sets the color, brightness, and saturation of a light.

        :param light_id: The ID of the light.
        :param hue: The hue value (0-65535).
        :param brightness: The brightness value (0-254).
        :param saturation: The saturation value (0-254).
        :return: The API response as a dictionary.
        """
        self.validate_color_values(hue, brightness, saturation)
        try:
            url = self.get_url(light_id)
            data = {
                "hue": hue,
                "bri": brightness,
                "sat": saturation
            }
            return await self.http.put(url, data)  # Await the async HTTP request
        except Exception as e:
            self.log_error(f"Failed to set light color for {light_id}: {str(e)}")
            raise e

    async def get_available_lights(self):
        """
        Retrieves the list of available lights from the bridge.

        :return: The list of lights as a dictionary.
        """
        try:
            url = f"http://{self.ip}/api/{self.token}/lights"
            return await self.http.get(url)  # Await the async HTTP request
        except Exception as e:
            self.log_error(f"Failed to retrieve available lights: {str(e)}")
            raise e

    def validate_light_id(self, light_id):
        """
        Validates the light ID.

        :param light_id: The light ID to validate.
        :raises: Exception if the light ID is invalid.
        """
        if not isinstance(light_id, str) or not light_id:
            self.log_error(f"Invalid light ID: {light_id}")
            raise Exception(f"Invalid light ID: {light_id}")

    def validate_color_values(self, hue, brightness, saturation):
        """
        Validates color values for lights.

        :param hue: The hue value.
        :param brightness: The brightness value.
        :param saturation: The saturation value.
        :raises: Exception if any value is out of range.
        """
        if not (0 <= hue <= 65535):
            self.log_error(f"Invalid hue value: {hue}. Expected range is 0 to 65535.")
            raise Exception(f"Invalid hue value: {hue}. Expected range is 0 to 65535.")
        if not (0 <= brightness <= 254):
            self.log_error(f"Invalid brightness value: {brightness}. Expected range is 0 to 254.")
            raise Exception(f"Invalid brightness value: {brightness}. Expected range is 0 to 254.")
        if not (0 <= saturation <= 254):
            self.log_error(f"Invalid saturation value: {saturation}. Expected range is 0 to 254.")
            raise Exception(f"Invalid saturation value: {saturation}. Expected range is 0 to 254.")

    def log_error(self, message):
        """
        Logs an error message to a file.

        :param message: The error message to log.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('bridge_error_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] {message}\n")