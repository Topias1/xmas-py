import json
import os
import random
import asyncio
from datetime import datetime
from bridge import Bridge
from dotenv import load_dotenv

class Animation:
    def __init__(self, bridge: Bridge, animation_file: str):
        """
        Initializes the Animation class with a Bridge instance and an animation configuration file.
        :param bridge: The Bridge instance to communicate with the Hue lights.
        :param animation_file: Path to the JSON file containing animation configurations.
        """
        load_dotenv()
        self.bridge = bridge
        self.lights = os.getenv('LIGHTS').split('|')
        self.minimum_duration = int(os.getenv('MIN_DURATION', 20))
        self.maximum_duration = int(os.getenv('MAX_DURATION', 200))

        self.animations = self.load_and_validate_animations(animation_file)

    def load_and_validate_animations(self, animation_file: str) -> dict:
        """
        Loads and validates the animation JSON configuration file.
        :param animation_file: Path to the JSON file.
        :return: Parsed and validated JSON data as a dictionary.
        """
        try:
            with open(animation_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise Exception(f"Animation file {animation_file} not found.")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in {animation_file}: {str(e)}")

        required_keys = ['speed', 'hue', 'bri', 'sat']
        for animation_name, properties in data.items():
            for key in required_keys:
                if key not in properties:
                    raise Exception(f"Missing key '{key}' in animation '{animation_name}'.")

                if not all(k in properties[key] for k in ['min', 'max']):
                    raise Exception(f"Missing 'min' or 'max' for '{key}' in animation '{animation_name}'.")

                if not isinstance(properties[key]['min'], int) or not isinstance(properties[key]['max'], int):
                    raise Exception(f"'min' and 'max' for '{key}' in animation '{animation_name}' must be integers.")

                if properties[key]['min'] > properties[key]['max']:
                    raise Exception(f"'min' must be less than 'max' for '{key}' in animation '{animation_name}'.")

        return data

    async def load_effect(self):
        """
        Loads a random animation effect on the lights defined in the configuration.
        """
        # Turn on all lights asynchronously
        tasks = [self.bridge.turn_on_light(light_id) for light_id in self.lights]
        await asyncio.gather(*tasks)

        animation_name = random.choice(list(self.animations.keys()))
        config = self.animations[animation_name]
        duration = random.randint(self.minimum_duration, self.maximum_duration)

        for _ in range(duration):
            tasks = []
            for light_id in self.lights:
                try:
                    state = self.generate_random_state(config)
                    self.debug_request(light_id, state)
                    # Add set light color to tasks
                    tasks.append(self.bridge.set_light_color(light_id, state["hue"], state["bri"], state["sat"]))
                except Exception as e:
                    self.log_error(f"Failed to update light {light_id}: {str(e)}")
            # Wait for all light color updates to finish
            await asyncio.gather(*tasks)
            await asyncio.sleep(config['speed']['min'] / 1000)  # Control the speed of the animation

    def generate_random_state(self, config: dict) -> dict:
        """
        Generates a random state for a light based on the animation configuration.
        :param config: The animation configuration dictionary.
        :return: A dictionary containing random hue, brightness, and saturation values.
        """
        return {
            "hue": random.randint(config['hue']['min'], config['hue']['max']),
            "bri": random.randint(config['bri']['min'], config['bri']['max']),
            "sat": random.randint(config['sat']['min'], config['sat']['max']),
        }

    def launch(self):
        """
        Launches an infinite animation loop on the lights.
        """
        while True:
            try:
                asyncio.run(self.load_effect())  # Run the effect asynchronously
            except Exception as e:
                self.log_error(f"Animation error: {str(e)}")
                print(f"An error occurred: {str(e)}")

    def debug_request(self, light_id: str, state: dict):
        """
        Outputs debug information for a light state request.
        :param light_id: The ID of the light.
        :param state: The state being set for the light.
        """
        print(f"Light ID: {light_id} | State: {state}")

    def debug_response(self, light_id: str, response: dict):
        """
        Outputs debug information for a light state response.
        :param light_id: The ID of the light.
        :param response: The response from the bridge.
        """
        print(f"Response for Light ID {light_id}: {response}")

    def log_error(self, message: str):
        """
        Logs an error message to a file.
        :param message: The error message to log.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('error_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] {message}\n")