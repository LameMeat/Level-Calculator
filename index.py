import logging
import src.config as config_module
import src.console as console_module
import src.matrix as matrix_module
from src.file_manager import FileManager
from src.shared_state import SharedState

# Configure logging
logging.basicConfig(filename='floor_level_calculator.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load menu options from JSON file
default_variables = FileManager.load_json('default_variables.json')
menu_options = FileManager.load_json('menu.json')

# Initialize shared state
shared_state = SharedState()

# Initialize Config, Console, and FileManager
config = config_module.Config(shared_state, default_variables)
console = console_module.Console(action_map={}, shared_state=shared_state)
file_manager = FileManager(console)
matrix = matrix_module.Matrix(config, file_manager)

# Action mappings
action_map = {
    "open_matrix_menu": lambda: console.navigate_menu(menu_options, "matrix_menu"),
    "calculate_floor_leveling_details": matrix.calculate_leveling_marker_heights,
    "save_current_matrix": matrix.save_matrix,
    "load_saved_matrix": matrix.load_saved_matrix,
    "settings": lambda: console.navigate_menu(menu_options, "settings_menu"),
    "about": lambda: console.navigate_menu(menu_options, "about"),
    "help": lambda: console.navigate_menu(menu_options, "help"),
    "exit": lambda: console.exit_program(),
    "input_points": matrix.input_points,
    "input_distances": matrix.input_distances,
    "show_current_matrix": lambda: (matrix.print_matrix(True), console.wait_for_input()),
    "delete_points": matrix.delete_points,
    "change_height_unit": lambda: config.modify_variable("height_unit"),
    "change_distance_unit": lambda: config.modify_variable("distance_unit"),
    "change_max_slope": lambda: config.modify_variable("max_slope"),
    "change_save_directory": lambda: config.modify_variable("save_directory"),
    "restore_default_settings": config.restore_default_settings,
    "back_to_main_menu": lambda: console.navigate_menu(menu_options, "main_menu"),
    "save_variable_changes": lambda: (config.save_variable_changes(), console.navigate_menu(menu_options, "main_menu")),
    "discard_variable_changes": lambda: (config.discard_variable_changes(), console.navigate_menu(menu_options, "main_menu")),
}

# Update Console with action_map
console.action_map = action_map

# Main program
if __name__ == "__main__":
    console.navigate_menu(menu_options, "main_menu")