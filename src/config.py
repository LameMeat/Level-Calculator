import logging
import json
from typing import Dict, Optional, Union

class Config:
    def __init__(self, default_variables: Optional[Dict[str, Union[float, str]]] = None, variable_file: str = "variables.json"):
        self.variable_file = variable_file
        self.default_variables = default_variables or {}
        self.current_variables = self.default_variables.copy()
        self.temp_variables = self.default_variables.copy()
        self.load_variables()

    def save_variable_changes(self) -> None:
        self.current_variables.update(self.temp_variables)
        try:
            with open(self.variable_file, "w") as f:
                if self.variable_file.endswith(".json"):
                    json.dump(self.current_variables, f, indent=4)
                else:
                    for key, value in self.current_variables.items():
                        f.write(f"{key}={value}\n")
            logging.info("Current variables saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save current variables: {e}")
            print(f"Failed to save current variables: {e}")

    def load_variables(self) -> None:
        try:
            with open(self.variable_file, "r") as f:
                if self.variable_file.endswith(".json"):
                    self.current_variables = json.load(f)
                else:
                    for line in f:
                        key, value = line.strip().split("=")
                        self.current_variables[key] = self._convert_value(value) # Convert value to float if possible
            self.temp_variables.update(self.current_variables)
            logging.info("Variables loaded successfully.")
        except FileNotFoundError:
            logging.warning("Variables file not found, using default variables.")
        except json.JSONDecodeError:
            logging.error("Error decoding JSON file.")
        except Exception as e:
            logging.error(f"Error loading variables: {e}")

    def restore_default_settings(self) -> None:
        self.current_variables.update(self.default_variables)
        self.temp_variables.update(self.current_variables)
        print("Default settings restored.")

    @staticmethod
    def _convert_value(value: str) -> Union[float, str]:
        try:
            return float(value)
        except ValueError:
            return value