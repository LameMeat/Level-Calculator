import sys
import os
import logging
import msvcrt
from datetime import datetime

# Configure logging
logging.basicConfig(filename='floor_level_calculator.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

default_variables = {
    "height_unit": "millimeters",
    "distance_unit": "inch",
    "max_slope": 0.044, # this values, .044mm/inch, was based on sources I found that said 3/16 over 10 feet or 1/8 over 6 feet- .044mm/inch is about right between those
    "save_folder": "saves",
}

current_variables = default_variables.copy()
temp_variables = current_variables.copy()

def load_variables():
    try:
        with open("variables.txt", "r") as f:
            for line in f:
                key, value = line.split("=")
                value = value.strip()
                try:
                    current_variables[key] = float(value)
                except ValueError:
                    current_variables[key] = value
        temp_variables.update(current_variables)
        logging.info("Variables loaded successfully.")
    except FileNotFoundError:
        logging.warning("Variables file not found, using default variables.")
        print("Variables file not found, using default variables.")
    except Exception as e:
        logging.error(f"Error loading variables: {e}")
        print(f"Error loading variables: {e}")

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

matrix = {}

class Distance:
    def __init__(self, point1, point2, distance: float):
        self.point1 = point1
        self.point2 = point2
        try:
            self.distance = float(distance)
        except ValueError:
            raise ValueError("Distance must be a float")

    def __str__(self):
        return f"{self.point1}-{self.point2}: {self.distance}"

class Point:
    def __init__(self, label, height: float):
        self.label = label
        self.height = height
        self.distances = {}
        self.target_thickness = 'X'

    def add_reference(self, point, distance: float):
        if point not in self.distances:
            self.distances[point] = Distance(self.label, point, distance)

    def __str__(self):
        return f"{self.label}: {self.height}"

# Menu Functions

## Main

def main_menu_choice(choice):
    try:
        menu = menu_options["main_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Open Matrix Menu":
                print_menu("matrix_menu", matrix_menu_choice)
            elif action == "Settings":
                print_menu("settings_menu", settings_menu_choice, settings_data)
            elif action == "Calculate Floor Leveling Details":
                calculate_leveling_marker_heights()
            elif action == "Save Current Matrix":
                save_matrix()
            elif action == "Load Saved Matrix":
                select_matrix_file()
            elif action == "Help":
                main_help()
            elif action == "About":
                print_menu("about_menu", lambda x: False)
                #wait_for_input()
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

def calculate_leveling_marker_heights():
    if len(matrix) < 2:
        print("You must have at least 2 points to calculate leveling marker heights.")
        wait_for_input()
        return
    sorted_points = sorted(matrix.values(), key=lambda x: x.height, reverse=True)
    no_change = False
    while True:
        no_change = True
        for point in sorted_points:
            if len(point.distances) == 0:
                continue
            for distance in point.distances.values():
                adjacent_point = matrix[distance.point2]
                if adjacent_point.target_thickness == 'X':
                    adjacent_point.target_thickness = 0.0
                target_height = point.height - (distance.distance * current_variables["max_slope"])
                target_thickness = round(target_height - adjacent_point.height, 2)
                if target_thickness > adjacent_point.target_thickness:
                    adjacent_point.target_thickness = target_thickness
                    no_change = False
                    print(f"Point {adjacent_point.label} target thickness updated to {adjacent_point.target_thickness}")
        if no_change:
            break
    print_matrix(False)
    wait_for_input()
    
def save_matrix():
    save_folder = current_variables["save_folder"]
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    # save the current matrix to a file
    time_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_file_name = f"matrix_{time_string}.mf"
    file_name = input(f"Enter file name to save the matrix (default: {default_file_name}): ").strip()
    if file_name == "":
        file_name = default_file_name
    if not file_name.endswith('.mf'):
        file_name += '.mf'
    try:
        with open(os.path.join(save_folder, file_name), 'w') as f:
            for point in matrix.values():
                f.write(f"{point.label} {point.height}\n")
                for distance in point.distances.values():
                    f.write(f"{distance.point1} {distance.point2} {distance.distance}\n")
        print(f"Matrix saved to {save_folder}\{file_name}\n")
    except Exception as e:
        logging.error(f"Error saving matrix: {e}")
        print(f"Error saving matrix: {e}")
    wait_for_input()

def select_matrix_file():
    save_folder = current_variables["save_folder"]
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    files = [f for f in os.listdir(save_folder) if f.endswith('.mf')]
    if not files:
        print("No saved matrices found.")
        wait_for_input()
        return
    print("Select a saved matrix file:")
    choice = prompt_for_save_choice(files, True)
    if choice == '':
        if confirm_escape():
            print("Exiting load menu.")
        return
    else:
        file_name = files[choice - 1]
        load_matrix(os.path.join(save_folder, file_name))

def prompt_for_save_choice(backup_folders, refresh: bool = False):
    if refresh:
        refresh_screen()
    print_and_dash("Load Matrix")
    for i, folder in enumerate(backup_folders):
        print(f"{i+1}. {folder}")
    choice = input("\nEnter the number of the backup to restore or hit enter to exit): ").strip()
    if choice.lower() == '':
        return ''
    try:
        choice = int(choice)
        if choice < 1 or choice > len(backup_folders):
            print("Invalid choice, please try again.")
            return prompt_for_save_choice(backup_folders)
        return choice
    except ValueError:
        print("Invalid choice, please try again.")
        return prompt_for_save_choice(backup_folders)    

def load_matrix(file):
    # load the matrix from a file
    points_buffer = {}
    distances_buffer = []
    try:
        with open(file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    label, height = parts
                    points_buffer[label] = float(height)
                elif len(parts) == 3:
                    point1, point2, distance = parts
                    distances_buffer.append((point1, point2, float(distance)))
        for label, height in points_buffer.items():
            matrix[label] = Point(label, height)
        
        for point1, point2, distance in distances_buffer:
            matrix[point1].add_reference(point2, distance)
            matrix[point2].add_reference(point1, distance)
        
        print(f"Matrix loaded from {file}")
        logging.info(f"Matrix loaded successfully from {file}")
    except Exception as e:
        logging.error(f"Error loading matrix: {e}")
        print(f"Error loading matrix: {e}")
    print_matrix(False)
    wait_for_input()

def main_help():
    refresh_screen()
    print_and_dash("\nLevel Calculator Help")
    print("Open Matrix Menu: Access the matrix input and management menu.")
    print("Calculate Floor Leveling Details: Calculate the leveling marker heights based on the current matrix.")
    print("Save Current Matrix: Save the current matrix to a file.")
    print("Load Saved Matrix: Load a saved matrix from a file.")
    print("Settings: Change application settings.")
    print("About: Information about the application and its author.")
    print("Help: Display this help message (also works in the matrix menu and settings menu).")
    print("Exit: Exit the application.")
    wait_for_input()

## Matrix

def delete_points():
    while True:
        refresh_screen()
        print_and_dash("Delete Points")
        print("Enter the point label to delete, then hit enter.")
        print_and_dash("Hit enter without entering a point to finish deleting points.")
        print_matrix(False)
        point_label = input("Enter point label to delete (or press Enter to finish): ").strip()
        if point_label == "":
            if confirm_escape():
                break
        if point_label in matrix:
            del matrix[point_label]
            distances = {k: v for k, v in distances.items() if point_label not in k}
            for k in list(distances.keys()):
                if point_label in k:
                    del distances[k]
            print(f"Point {point_label} deleted.")
        else:
            print(f"Point {point_label} not found.")
        wait_for_input()

def input_points():
    while True:
        refresh_screen()
        print_and_dash("Input Points")
        print("Enter the point label, then hit enter.")
        print("You will then be prompted for the height of the point.")
        print_and_dash("Hit enter without entering a point/height to finish inputting points.")
        current_points = ", ".join(f"{key}: {value.height}" for key, value in matrix.items())
        print(f"Current points: {current_points}\n")
        
        point_label = validate_input("Enter point label (or press Enter to finish): ", lambda x: x != "", "Invalid point label.")
        if point_label is None:
            break
        elif point_label == "":
            continue
        
        height = validate_input(f"Enter height for point {point_label}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid height. Please enter a number.")
        if height is None:
            break
        
        matrix[point_label] = Point(point_label, float(height))
        print(f"Point {point_label} with height {height} added.")

def input_distances():
    while True:
        if len(matrix) < 2:
            print("You must have at least 2 points to enter a distance.")
            wait_for_input()
            break
        refresh_screen()
        print_and_dash("Input Distances")
        print("Enter the first point, then the second point, then the distance between them.")
        print("You will then be prompted for the distance.")
        print("\nNote: the points must have been entered with their heights before you can enter distances.")
        print_and_dash("Hit enter without entering a point/distance to finish inputting distances.")
        print_matrix(False)
        
        point1_label = validate_input("Enter first point (or press Enter to finish): ", check_for_points, "Point not found.")
        if point1_label is None:
            break
        elif point1_label == "":
            continue
        
        point2_label = validate_input(f"Enter second point (or press Enter to finish): ", check_for_points, "Point not found.")
        if point2_label is None:
            break
        elif point2_label == "":
            continue
        
        distance = validate_input(f"Enter distance between {point1_label} and {point2_label}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid distance. Please enter a number.")
        if distance is None:
            break
        elif distance == "":
            continue
        
        matrix[point1_label].add_reference(point2_label, float(distance))
        matrix[point2_label].add_reference(point1_label, float(distance))
        print(f"Distance between {point1_label} and {point2_label} with distance {distance} added.")

def check_for_points(point_label):
    return point_label in matrix

def print_points(refresh: bool = False):
    if refresh:
        refresh_screen()
    print_and_dash("Current Points")
    for point in matrix.values():
        if point == list(matrix.values())[-1]:
            print_and_dash(str(point))
        else:
            print(str(point))

def print_distances(refresh: bool = False):
    if refresh:
        refresh_screen()
    print_and_dash("Current Distances")
    for point in matrix.values():
        for distance in point.distances.values():
            print(str(distance))

def print_matrix(refresh: bool = False, tab_size: int = 10):
    if len(matrix) == 0:
        print("No points in the matrix.")
    if refresh:
        refresh_screen()
    print_and_dash("Current Matrix")
    
    point_labels = list(matrix.keys())
    
    # Print point labels and heights in the top row of the table
    header_row = ["heights: "] + [""] + [f"{point}:{matrix[point].height}{current_variables['height_unit']}" for point in point_labels]
    print("\t".join(header_row).expandtabs(tab_size))
    
    # Print distances for each point
    for point1 in point_labels:
        distances_row = [""] + [point1] + [f"{matrix[point1].distances[point2].distance}{current_variables['distance_unit']}" 
                                    if point2 in matrix[point1].distances else " " 
                                    for point2 in point_labels]
        print("\t".join(distances_row).expandtabs(tab_size))

    footer_row = ["delta: "] + [""] + [f"{point}:{matrix[point].target_thickness}{current_variables['height_unit']}" for point in point_labels]
    print("\t".join(footer_row).expandtabs(tab_size))

def matrix_menu_choice(choice):
    try:
        menu = menu_options["matrix_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Input Points":
                input_points()
            elif action == "Input Distances":
                input_distances()
            elif action == "Show Current Matrix":
                print_matrix(True)
                wait_for_input()
            elif action == "Delete Points":
                delete_points()
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
    print_and_dash("\nMatrix Menu Help")
    print("Input Points: Input points and their heights.")
    print("Input Distances: Input distances between points.")
    print("Show Current Matrix: Show the current matrix of points and distances.")
    print("Delete Points: Delete points from the matrix.")
    print("Back to Main Menu: Return to the main menu.")
    wait_for_input()


## Settings

def save_variable_changes():
    current_variables.update(temp_variables)
    try:
        with open("variables.txt", "w") as f:
            for key in current_variables:
                f.write(f"{key}={current_variables[key]}\n")
        logging.info("Current variables saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save current variables: {e}")
        print(f"Failed to save current variables: {e}")
    
def restore_default_settings():
    current_variables.update(default_variables)
    temp_variables.update(current_variables)
    print("Default settings restored.")
    wait_for_input()

def set_max_slope():
    print("The current max slope is set to: ", temp_variables["max_slope"])
    max_slope = validate_input(f"Enter new max slope in {temp_variables['height_unit']}/{temp_variables['distance_unit']}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid slope. Please enter a number.")
    if max_slope is not None:
        max_slope = float(max_slope)
    if max_slope is not None:
        temp_variables["max_slope"] = float(max_slope)
        print(f"Max slope set to {max_slope}.")
        wait_for_input()

def set_height_unit():
    print("The current height unit is set to: ", temp_variables["height_unit"])
    height_unit = validate_input("Enter height unit (e.g., millimeters, centimeters, inches): ", lambda x: x != "", "Invalid height unit.")
    if height_unit is not None:
        temp_variables["height_unit"] = height_unit
        print(f"Height unit set to {height_unit}.")
        wait_for_input()

def set_distance_unit():
    print("The current distance unit is set to: ", temp_variables["distance_unit"])
    distance_unit = validate_input("Enter distance unit (e.g., meters, kilometers, feet): ", lambda x: x != "", "Invalid distance unit.")
    if distance_unit is not None:
        temp_variables["distance_unit"] = distance_unit
        print(f"Distance unit set to {distance_unit}.")
        wait_for_input()

def set_save_folder():
    print("The current save folder is set to: ", temp_variables["save_folder"])
    save_folder = validate_input("Enter save folder: ", lambda x: os.path.isdir(x), "Invalid save folder name or directory does not exist")
    if save_folder is not None:
        temp_variables["save_folder"] = save_folder
        print(f"Save folder set to {save_folder}.")
        wait_for_input()

def format_variable(key, current_value, temp_value, unit=""):
    if current_value != temp_value:
        return f"{key}: {current_value}{unit} -> {temp_value}{unit}\n"
    else:
        return f"{key}: {current_value}{unit}\n"

def settings_data():
    menu_data = "Settings:\n"
    for key in current_variables:
        if key == "max_slope":
            current_value = f"{current_variables[key]}{current_variables['height_unit']}/{current_variables['distance_unit']}"
            temp_value = f"{temp_variables[key]}{temp_variables['height_unit']}/{temp_variables['distance_unit']}"
            menu_data += format_variable(key, current_value, temp_value)
        else:
            menu_data += format_variable(key, current_variables[key], temp_variables[key])
    return menu_data

def settings_menu_choice(choice):
    stay_in_current_menu = True
    # print the current_variables and, if they are different, the temp_variables in a format like "current -> temp"
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
                save_variable_changes()
                stay_in_current_menu = False
            elif action == "Restore default settings":
                restore_default_settings()
            elif action == "Exit Without Saving":
                logging.debug("Exiting the settings menu without saving changes.")
                temp_variables.update(current_variables)
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
    # check if temp_variables are different from current_variables and update the menu to reflect that
    logging.debug(f"temp_variables: {temp_variables}, current_variables: {current_variables}")
    if temp_variables != current_variables:
        menu_options["settings_menu"].pop("9", None)
        menu_options["settings_menu"]["5"] = "Save & Return to Main Menu"
        menu_options["settings_menu"]["9"] = "Exit Without Saving"
    else:
        menu_options["settings_menu"].pop("5", None)
        menu_options["settings_menu"].pop("9", None)
        menu_options["settings_menu"]["9"] = "Back to Main Menu"
    return stay_in_current_menu

def settings_help():
    print_and_dash("\nSettings Menu Help")
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
    wait_for_input()

# Generic Menu Functions

def print_menu(menu_name, menu_callback, menu_data_function=None):
    stay_in_current_menu = True
    while stay_in_current_menu:
        refresh_screen()
        menu = menu_options[menu_name]
        # sort the menu by the keys
        menu = dict(sorted(menu.items()))
        print_and_dash(menu['Title'])
        for key in menu:
            if key != "Title" and key[0] != "*":
                print(f"{key}. {menu[key]}")
        print()
        if menu_data_function:
            menu_data = menu_data_function()
            if menu_data:
                print(menu_data)
        choice = input("Enter choice: ").strip()
        stay_in_current_menu = menu_callback(choice)

def refresh_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_and_dash(string):
    print(string)
    print("-" * len(string), "\n")

def wait_for_input():
    input("Press Enter to continue...")

def confirm_escape():
    print("Hit enter again to confirm escape, or type anything else to remain")
    key = msvcrt.getch()
    if key == b'\r':  # Enter key
        return True
    else:
        return False
    
def validate_input(prompt, validation_func, error_message):
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            if confirm_escape():
                return None
            else:
                return ""
        if validation_func(user_input):
            return user_input
        else:
            print(error_message)
            wait_for_input()

# Main program

if __name__ == "__main__":
    load_variables()
    print_menu("main_menu", main_menu_choice)
    print("Exiting...")
    logging.info("Exiting application.")
    sys.exit()