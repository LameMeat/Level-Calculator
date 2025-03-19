from .console import Console
import os
import logging
from datetime import datetime
from src import config

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

def calculate_leveling_marker_heights():
    if len(matrix) < 2:
        print("You must have at least 2 points to calculate leveling marker heights.")
        Console.wait_for_input()
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
                target_height = point.height - (distance.distance * config.current_variables["max_slope"])
                target_thickness = round(target_height - adjacent_point.height, 2)
                if target_thickness > adjacent_point.target_thickness:
                    adjacent_point.target_thickness = target_thickness
                    no_change = False
                    print(f"Point {adjacent_point.label} target thickness updated to {adjacent_point.target_thickness}")
        if no_change:
            break
    print_matrix(False)
    Console.wait_for_input()

def save_matrix():
    save_folder = config.current_variables["save_folder"]
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
    Console.wait_for_input()

def prompt_for_save_choice(backup_folders, refresh: bool = False):
    if refresh:
        Console.refresh_screen()
    Console.print_and_dash("Load Matrix")
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

def select_matrix_file():
    save_folder = config.current_variables["save_folder"]
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    files = [f for f in os.listdir(save_folder) if f.endswith('.mf')]
    if not files:
        print("No saved matrices found.")
        Console.wait_for_input()
        return
    print("Select a saved matrix file:")
    choice = prompt_for_save_choice(files, True)
    if choice == '':
        if Console.confirm_escape():
            print("Exiting load menu.")
        return
    else:
        file_name = files[choice - 1]
        load_matrix(os.path.join(save_folder, file_name))

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
    Console.wait_for_input()


def print_points(refresh: bool = False):
    if refresh:
        Console.refresh_screen()
    Console.print_and_dash("Current Points")
    for point in matrix.values():
        if point == list(matrix.values())[-1]:
            Console.print_and_dash(str(point))
        else:
            print(str(point))

def print_distances(refresh: bool = False):
    if refresh:
        Console.refresh_screen()
    Console.print_and_dash("Current Distances")
    for point in matrix.values():
        for distance in point.distances.values():
            print(str(distance))

def print_matrix(refresh: bool = False, tab_size: int = 10):
    if len(matrix) == 0:
        print("No points in the matrix.")
    if refresh:
        Console.refresh_screen()
    Console.print_and_dash("Current Matrix")
    
    point_labels = list(matrix.keys())
    
    # Print point labels and heights in the top row of the table
    header_row = ["heights: "] + [""] + [f"{point}:{matrix[point].height}{config.current_variables['height_unit']}" for point in point_labels]
    print("\t".join(header_row).expandtabs(tab_size))
    
    # Print distances for each point
    for point1 in point_labels:
        distances_row = [""] + [point1] + [f"{matrix[point1].distances[point2].distance}{config.current_variables['distance_unit']}" 
                                    if point2 in matrix[point1].distances else " " 
                                    for point2 in point_labels]
        print("\t".join(distances_row).expandtabs(tab_size))

    footer_row = ["delta: "] + [""] + [f"{point}:{matrix[point].target_thickness}{config.current_variables['height_unit']}" for point in point_labels]
    print("\t".join(footer_row).expandtabs(tab_size))

def delete_points():
    while True:
        Console.refresh_screen()
        Console.print_and_dash("Delete Points")
        print("Enter the point label to delete, then hit enter.")
        Console.print_and_dash("Hit enter without entering a point to finish deleting points.")
        matrix.print_matrix(False)
        point_label = input("Enter point label to delete (or press Enter to finish): ").strip()
        if point_label == "":
            if Console.confirm_escape():
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
        Console.wait_for_input()

def input_points():
    while True:
        Console.refresh_screen()
        Console.print_and_dash("Input Points")
        print("Enter the point label, then hit enter.")
        print("You will then be prompted for the height of the point.")
        Console.print_and_dash("Hit enter without entering a point/height to finish inputting points.")
        current_points = ", ".join(f"{key}: {value.height}" for key, value in matrix.items())
        print(f"Current points: {current_points}\n")
        
        point_label = Console.validate_input("Enter point label (or press Enter to finish): ", lambda x: x != "", "Invalid point label.")
        if point_label is None:
            break
        elif point_label == "":
            continue
        
        height = Console.validate_input(f"Enter height for point {point_label}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid height. Please enter a number.")
        if height is None:
            break
        
        matrix[point_label] = Point(point_label, float(height))
        print(f"Point {point_label} with height {height} added.")

def input_distances():
    while True:
        if len(matrix) < 2:
            print("You must have at least 2 points to enter a distance.")
            Console.wait_for_input()
            break
        Console.refresh_screen()
        Console.print_and_dash("Input Distances")
        print("Enter the first point, then the second point, then the distance between them.")
        print("You will then be prompted for the distance.")
        print("\nNote: the points must have been entered with their heights before you can enter distances.")
        Console.print_and_dash("Hit enter without entering a point/distance to finish inputting distances.")
        matrix.print_matrix(False)
        
        point1_label = Console.validate_input("Enter first point (or press Enter to finish): ", check_for_points, "Point not found.")
        if point1_label is None:
            break
        elif point1_label == "":
            continue
        
        point2_label = Console.validate_input(f"Enter second point (or press Enter to finish): ", check_for_points, "Point not found.")
        if point2_label is None:
            break
        elif point2_label == "":
            continue
        
        distance = Console.validate_input(f"Enter distance between {point1_label} and {point2_label}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid distance. Please enter a number.")
        if distance is None:
            break
        elif distance == "":
            continue
        
        matrix[point1_label].add_reference(point2_label, float(distance))
        matrix[point2_label].add_reference(point1_label, float(distance))
        print(f"Distance between {point1_label} and {point2_label} with distance {distance} added.")

def check_for_points(point_label):
    return point_label in matrix