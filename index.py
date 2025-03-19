import sys
import os
import logging
import src.config as Config
from src.console import Console
import src.matrix as matrix
from src.matrix import Point, Distance

# Configure logging
logging.basicConfig(filename='floor_level_calculator.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

default_variables = {
            "height_unit": "millimeters",
            "distance_unit": "inch",
            "max_slope": 0.044, # this values, .044mm/inch, was based on sources I found that said 3/16 over 10 feet or 1/8 over 6 feet- .044mm/inch is about right between those
            "save_folder": "saves",
        }

# Menu options
menu_options = {
    "main_menu": {
        "Title": "Floor Leveling Calculator",
        "1": "Open Matrix Menu",
        "2": "Calculate Floor Leveling Details",
        "3": "Save Current Matrix",
        "4": "Load Saved Matrix",
        "5": "Settings",
        "6": "About",
        "7": "Help",
        "9": "Exit",
    },
    "matrix_menu": {
        "Title": "Matrix Input Menu",
        "1": "Input Points",
        "2": "Input Distances",
        "3": "Show Current Matrix",
        "5": "Delete Points",
        "9": "Back to Main Menu",
    },
    "settings_menu": {
        "Title": "Settings Menu",
        "1": "Change Height Unit",
        "2": "Change Distance Unit",
        "3": "Change Max Slope",
        "4": "Change Save Folder",
        #"5": "Save & Return to Main Menu",
        "7": "Restore default settings",
        #"9": "Exit Without Saving",
        "9": "Back to Main Menu",
    },
    "about_menu": {
        "Title": "About",
        "10": "Author: Matthew Eater",
        "20": "I made this one day when I was working on a floor leveling project and thought it would be nice to have a calculator to help me out.",
        "30": "The basic principal is that you use a laser level to determine the relative heights of the high and low spots in the floor, measure the distances between those points, and then input that data into this calculator to get the thickness of the leveling compound to use at each point.",
        "40": "Eventually I want to add a feature that calculates the volume of compound required, but I think this will require either a more complex system for inputting points via a coordinate system, or it will require the user to only take measures that create triangles so that the topology of the floor can be calculated trigonomically.",
        "50": "This is a work in progress, and I welcome any feedback or suggestions for improvement.",
        "60": "Thanks for using my calculator!",
        "70": "...",
        "80": "This isn't a real menu, so just hit enter to return to the main menu.",
    },
}

Config = Config.Config(default_variables)

# Menu Functions

## Main

def main_menu_choice(choice):
    try:
        menu = menu_options["main_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Open Matrix Menu":
                Console.print_menu(menu_options, "matrix_menu", matrix_menu_choice)
            elif action == "Settings":
                Console.print_menu(menu_options, "settings_menu", settings_menu_choice, settings_data)
            elif action == "Calculate Floor Leveling Details":
                matrix.calculate_leveling_marker_heights()
            elif action == "Save Current Matrix":
                matrix.save_matrix()
            elif action == "Load Saved Matrix":
                matrix.select_matrix_file()
            elif action == "Help":
                main_help()
            elif action == "About":
                Console.print_menu(menu_options, "about_menu", lambda x: False)
                #Console.wait_for_input()
            elif action == "Exit":
                return False
            else:
                print("Invalid choice, please try again.")
        elif choice.lower() == 'help':
            main_help()
        else:
            print("Invalid choice, please try again.")
    except Exception as e:
        logging.error(f"Error in main_menu_choice: {e}")
        print(f"Error: {e}")
    return True

def main_help():
    Console.refresh_screen()
    Console.print_and_dash("\nLevel Calculator Help")
    print("Open Matrix Menu: Access the matrix input and management menu.")
    print("Calculate Floor Leveling Details: Calculate the leveling marker heights based on the current matrix.")
    print("Save Current Matrix: Save the current matrix to a file.")
    print("Load Saved Matrix: Load a saved matrix from a file.")
    print("Settings: Change application settings.")
    print("About: Information about the application and its author.")
    print("Help: Display this help message (also works in the matrix menu and settings menu).")
    print("Exit: Exit the application.")
    Console.wait_for_input()

## Matrix

def matrix_menu_choice(choice):
    try:
        menu = menu_options["matrix_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Input Points":
                matrix.input_points()
            elif action == "Input Distances":
                matrix.input_distances()
            elif action == "Show Current Matrix":
                matrix.print_matrix(True)
                Console.wait_for_input()
            elif action == "Delete Points":
                matrix.delete_points()
            elif action == "Back to Main Menu":
                return False
            else:
                print("Invalid choice, please try again.")
        elif choice.lower() == 'help':
            matrix_help()
        else:
            print("Invalid choice, please try again.")
    except Exception as e:
        logging.error(f"Error in matrix_menu_choice: {e}")
        print(f"Error: {e}")
    return True

def matrix_help():
    Console.print_and_dash("\nMatrix Menu Help")
    print("Input Points: Input points and their heights.")
    print("Input Distances: Input distances between points.")
    print("Show Current Matrix: Show the current matrix of points and distances.")
    print("Delete Points: Delete points from the matrix.")
    print("Back to Main Menu: Return to the main menu.")
    Console.wait_for_input()


## Settings

def set_max_slope():
    print("The current max slope is set to: ", Config.temp_variables["max_slope"])
    max_slope = Console.validate_input(f"Enter new max slope in {Config.temp_variables['height_unit']}/{Config.temp_variables['distance_unit']}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid slope. Please enter a number.")
    if max_slope is not None:
        max_slope = float(max_slope)
    if max_slope is not None:
        Config.temp_variables["max_slope"] = float(max_slope)
        print(f"Max slope set to {max_slope}.")
        Console.wait_for_input()

def set_height_unit():
    print("The current height unit is set to: ", Config.temp_variables["height_unit"])
    height_unit = Console.validate_input("Enter height unit (e.g., millimeters, centimeters, inches): ", lambda x: x != "", "Invalid height unit.")
    if height_unit is not None:
        Config.temp_variables["height_unit"] = height_unit
        print(f"Height unit set to {height_unit}.")
        Console.wait_for_input()

def set_distance_unit():
    print("The current distance unit is set to: ", Config.temp_variables["distance_unit"])
    distance_unit = Console.validate_input("Enter distance unit (e.g., meters, kilometers, feet): ", lambda x: x != "", "Invalid distance unit.")
    if distance_unit is not None:
        Config.temp_variables["distance_unit"] = distance_unit
        print(f"Distance unit set to {distance_unit}.")
        Console.wait_for_input()

def set_save_folder():
    print("The current save folder is set to: ", Config.temp_variables["save_folder"])
    save_folder = Console.validate_input("Enter save folder: ", lambda x: os.path.isdir(x), "Invalid save folder name or directory does not exist")
    if save_folder is not None:
        Config.temp_variables["save_folder"] = save_folder
        print(f"Save folder set to {save_folder}.")
        Console.wait_for_input()

def format_variable(key, current_value, temp_value, unit=""):
    if current_value != temp_value:
        return f"{key}: {current_value}{unit} -> {temp_value}{unit}\n"
    else:
        return f"{key}: {current_value}{unit}\n"

def settings_data():
    menu_data = "Settings:\n"
    for key in Config.current_variables:
        if key == "max_slope":
            current_value = f"{Config.current_variables[key]}{Config.current_variables['height_unit']}/{Config.current_variables['distance_unit']}"
            temp_value = f"{Config.temp_variables[key]}{Config.temp_variables['height_unit']}/{Config.temp_variables['distance_unit']}"
            menu_data += format_variable(key, current_value, temp_value)
        else:
            menu_data += format_variable(key, Config.current_variables[key], Config.temp_variables[key])
    return menu_data

def settings_menu_choice(choice):
    stay_in_current_menu = True
    # print the Config.current_variables and, if they are different, the Config.temp_variables in a format like "current -> temp"
    try:
        menu = menu_options["settings_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Change Height Unit":
                set_height_unit()
            elif action == "Change Distance Unit":
                set_distance_unit()
            elif action == "Change Max Slope":
                set_max_slope()
            elif action == "Change Save Folder":
                set_save_folder()
            elif action == "Save & Return to Main Menu":
                Config.save_variable_changes()
                stay_in_current_menu = False
            elif action == "Restore default settings":
                Config.restore_default_settings()
            elif action == "Exit Without Saving":
                logging.debug("Exiting the settings menu without saving changes.")
                Config.temp_variables.update(Config.current_variables)
                stay_in_current_menu = False
            elif action == "Back to Main Menu":
                stay_in_current_menu = False
            else:
                print("Invalid choice, please try again.")
        elif choice.lower() == 'help':
            settings_help()
        else:
            print("Invalid choice, please try again.")
    except Exception as e:
        logging.error(f"Error in settings_menu_choice: {e}")
        print(f"Error: {e}")
    # check if Config.temp_variables are different from Config.current_variables and update the menu to reflect that
    logging.debug(f"Config.temp_variables: {Config.temp_variables}, Config.current_variables: {Config.current_variables}")
    if Config.temp_variables != Config.current_variables:
        menu_options["settings_menu"].pop("9", None)
        menu_options["settings_menu"]["5"] = "Save & Return to Main Menu"
        menu_options["settings_menu"]["9"] = "Exit Without Saving"
    else:
        menu_options["settings_menu"].pop("5", None)
        menu_options["settings_menu"].pop("9", None)
        menu_options["settings_menu"]["9"] = "Back to Main Menu"
    return stay_in_current_menu

def settings_help():
    Console.print_and_dash("\nSettings Menu Help")
    print("Change Height Unit: Change the unit used for height.")
    print("Change Distance Unit: Change the unit used for distance.")
    print("Change Max Slope: Change the maximum slope allowed by the calculator.")
    print("Change Save Folder: Change the folder where saved matrices are stored.")
    print("Restore default settings: Restore the default settings (mm, inches, .044mm/inch).")
    print("-- If you have made changes to the settings you will see: --")
    print("Save & Return to Main Menu: Save the changes and return to the main menu.")
    print("Exit Without Saving: Exit the settings menu without saving changes.")
    print("-- If you have not made changes to the settings you will see: --")
    print("Back to Main Menu: Return to the main menu.")
    Console.wait_for_input()

# Generic Menu Functions


# Main program

if __name__ == "__main__":
    Console.print_menu(menu_options, "main_menu", main_menu_choice)
    print("Exiting...")
    logging.info("Exiting application.")
    sys.exit()