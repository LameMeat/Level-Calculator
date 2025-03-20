import logging
import json
import os
from typing import Dict, Optional, Union
from .console import Console
from .shared_state import SharedState

class Config:
    def __init__(self, shared_state: SharedState, default_variables: Optional[Dict[str, Union[float, str]]] = None, variable_file: str = "variables.json"):
        self.shared_state = shared_state
        self.variable_file = variable_file
        self.default_variables = default_variables or {}
        self.current_variables = self.default_variables.copy()
        self.temp_variables = self.default_variables.copy()
        self.load_variables()

    def save_variables(self, variables: Optional[Dict[str, Union[float, str]]] = None) -> None:
        variables_to_save = variables or self.current_variables
        try:
            with open(self.variable_file, "w") as f:
                if self.variable_file.endswith(".json"):
                    json.dump(variables_to_save, f, indent=4)
                else:
                    for key, value in variables_to_save.items():
                        f.write(f"{key}={value}\n")
            logging.info("Variables saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save variables: {e}")
            print(f"Failed to save variables: {e}")

    def save_variable_changes(self) -> None:
        self.current_variables.update(self.temp_variables)
        self.save_variables()
        self.shared_state.variables_changed = False

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
            logging.warning("Variables file not found, saving default variables.")
            self.save_variables(self.default_variables)
        except json.JSONDecodeError:
            logging.error("Error decoding JSON file.")
        except Exception as e:
            logging.error(f"Error loading variables: {e}")

    def restore_default_settings(self) -> None:
        self.current_variables.update(self.default_variables)
        self.temp_variables.update(self.current_variables)
        print("Default settings restored.")

    def modify_variable(self, key: str) -> None:
        if key not in self.current_variables:
            logging.error(f"Variable '{key}' does not exist.")
            return

        variable_info = self.current_variables[key]
        variable_type = variable_info.get("type")
        nullable = variable_info.get("nullable", False)

        current_value = self.current_variables[key]["value"]
        logging.info(f"Current value of '{key}': {current_value}")
        print(f"Current value of '{key}': {current_value}")

        def validate_input(value):
            if value is None and not nullable:
                logging.error(f"Variable '{key}' cannot be null.")
                return False
            if variable_type == "number":
                try:
                    float(value)
                    return True
                except ValueError:
                    logging.error(f"Invalid value for '{key}'. Expected a number.")
                    return False
            elif variable_type == "string":
                return isinstance(value, str)
            elif variable_type == "dir":
                return os.path.isdir(value)
            return False

        new_value = Console.validate_input(f"Enter new value for '{key}': ", validate_input, f"Invalid value for '{key}'.")

        if new_value is None:
            return

        if variable_type == "number":
            new_value = float(new_value)

        self.temp_variables[key]["value"] = new_value
        self.shared_state.variables_changed = True
        logging.info(f"Variable '{key}' updated to {new_value}.")

    def discard_variable_changes(self) -> None:
        self.temp_variables = self.current_variables.copy()

    @staticmethod
    def _convert_value(value: str) -> Union[float, str]:
        try:
            return float(value)
        except ValueError:
            return value