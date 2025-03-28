import os
import logging
import math
import numpy as np
from datetime import datetime
from .console import Console
from .config import Config
from .point import Point
from .file_manager import FileManager

class Matrix:
    def __init__(self, config: Config, file_manager: FileManager):
        self.config = config
        self.file_manager = file_manager
        self.matrix = {}

    def calculate_leveling_volume(self):
        if len(self.matrix) < 3:
            print("You must have at least 3 points to calculate leveling volume.")
            Console.wait_for_input()
            return
        # check if all points have a target thickness
        for point in self.matrix.values():
            if point.target_thickness == 'X':
                point.target_thickness = 0.0
        triangle_names = [] # list of unique triangle names, i.e. ab-ac-bc
        total_volume = 0.0
        for point1 in self.matrix.values():
            for dist1 in point1.distances.values():
                point2 = self.matrix[dist1.point2]
                for dist2 in point2.distances.values():
                    point3 = self.matrix[dist2.point2]
                    # make sure each point is unique
                    if point1 == point2 or point1 == point3 or point2 == point3:
                        continue
                    # make sure point 3 is contiguous with point 1
                    if point3 not in point1.distances.values():
                        continue
                    triangle_name = f"{point1.label}-{point2.label}-{point3.label}"
                    if triangle_name in triangle_names:
                        continue
                    triangle_names.append(triangle_name)
                    # calculate the volume of the prism
                    volume = self.calculate_prism_volume(point1, point2, point3)
                    total_volume += volume
                    print(f"Triangle {triangle_name} volume: {volume}")
        print(f"Total leveling volume: {total_volume}")
        Console.wait_for_input()

    def calculate_prism_volume(self, point1, point2, point3):
        # calculate the volume of the prism using the heights and target thicknesses of the points to determine the vertices of 3 non-overlapping tetrahedrons

        prism = {
            'a' : point1.height,
            'b' : point2.height,
            'c' : point3.height,
            'd' : point1.target_thickness,
            'e' : point2.target_thickness,
            'f' : point3.target_thickness,
            'ab' : point1.distances[point2.label].distance,
            'ac' : point1.distances[point3.label].distance,
            'bc' : point2.distances[point3.label].distance
        }

        return self.prism_volume(prism)

    def heron_area(a, b, c):
        s = (a + b + c) / 2  # Semi-perimeter
        return math.sqrt(s * (s - a) * (s - b) * (s - c))

    def prism_volume(prism):
        # Extract base heights
        a, b, c = prism['a'], prism['b'], prism['c']
        d, e, f = prism['d'], prism['e'], prism['f']
        
        # Base triangle side lengths
        ab, ac, bc = prism['ab'], prism['ac'], prism['bc']

        # Assume 2D coordinates for base triangle using simple planar embedding
        A = (0, 0, a)  # Place first point at origin
        B = (ab, 0, b)  # Place second point along x-axis
        C_x = (ac**2 - bc**2 + ab**2) / (2 * ab)  # Compute third point's x-coordinate
        C_y = math.sqrt(max(0, ac**2 - C_x**2))   # Compute y-coordinate
        C = (C_x, C_y, c)  # Third point in 3D space

        # Compute top points with offsets
        A_top = (0, 0, a + d)
        B_top = (ab, 0, b + e)
        C_top = (C_x, C_y, c + f)

        # Tetrahedral decomposition (three tetrahedra inside the prism)
        V1 = tetrahedron_volume(A, B, C, A_top)
        V2 = tetrahedron_volume(B, C, A_top, B_top)
        V3 = tetrahedron_volume(C, A_top, B_top, C_top)

        # Total volume is the sum of the three tetrahedra
        return V1 + V2 + V3
    
    def tetrahedron_volume(p1, p2, p3, p4):
        A = np.array(p1)
        B = np.array(p2)
        C = np.array(p3)
        D = np.array(p4)

        # Compute vectors
        AB = B - A
        AC = C - A
        AD = D - A

        # Compute scalar triple product (|AB x AC . AD| / 6)
        cross_product = np.cross(AB, AC)
        volume = abs(np.dot(cross_product, AD)) / 6.0
        return volume

    def calculate_leveling_marker_heights(self):
        if len(self.matrix) < 2:
            print("You must have at least 2 points to calculate leveling marker heights.")
            Console.wait_for_input()
            return
        sorted_points = sorted(self.matrix.values(), key=lambda x: x.height, reverse=True)
        no_change = False
        while True:
            no_change = True
            for point in sorted_points:
                if len(point.distances) == 0:
                    continue
                for distance in point.distances.values():
                    adjacent_point = self.matrix[distance.point2]
                    if adjacent_point.target_thickness == 'X':
                        adjacent_point.target_thickness = 0.0
                    target_height = point.height - (distance.distance * self.config.current_variables["max_slope"]["value"])
                    target_thickness = round(target_height - adjacent_point.height, 2)
                    if target_thickness > adjacent_point.target_thickness:
                        adjacent_point.target_thickness = target_thickness
                        no_change = False
                        print(f"Point {adjacent_point.label} target thickness updated to {adjacent_point.target_thickness}")
            if no_change:
                break
        self.print_matrix(False)
        Console.wait_for_input()

    def save_matrix(self):
        save_directory = self.config.current_variables["save_directory"]["value"]
        print(f"Current save directory: {save_directory}")
        FileManager.ensure_directory_exists(save_directory)
        # save the current matrix to a file
        time_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_file_name = f"matrix_{time_string}.mf"
        file_name = input(f"Enter file name to save the matrix (default: {default_file_name}): ").strip()
        if file_name == "":
            file_name = default_file_name
        if not file_name.endswith('.mf'):
            file_name += '.mf'
        try:
            content = ""
            for point in self.matrix.values():
                content += f"{point.label} {point.height}\n"
                for distance in point.distances.values():
                    content += f"{distance.point1} {distance.point2} {distance.distance}\n"
            FileManager.save_file(os.path.join(save_directory, file_name), content)
            print(f"Matrix saved to {save_directory}\{file_name}\n")
        except Exception as e:
            logging.error(f"Error saving matrix: {e}")
            print(f"Error saving matrix: {e}")
        Console.wait_for_input()

    def load_saved_matrix(self):
        save_directory = self.config.current_variables["save_directory"]["value"]
        FileManager.ensure_directory_exists(save_directory)
        files = FileManager.list_files(save_directory, '.mf')
        if not files:
            print("No saved matrices found.")
            Console.wait_for_input()
            return
        print("Select a saved matrix file:")
        choice = FileManager.prompt_for_file_choice(self.file_manager, save_directory)
        if choice == '':
            if Console.confirm_escape():
                print("Exiting load menu.")
            return
        else:
            file_name = choice['text']
            file_path = os.path.join(save_directory, file_name)
            content = FileManager.load_file(file_path)
            if content is None:
                print(f"Error loading matrix from {file_path}")
                logging.error(f"Error loading matrix from {file_path}")
                return

            points_buffer = {}
            distances_buffer = []
            try:
                for line in content.splitlines():
                    parts = line.strip().split()
                    if len(parts) == 2:
                        label, height = parts
                        points_buffer[label] = float(height)
                    elif len(parts) == 3:
                        point1, point2, distance = parts
                        distances_buffer.append((point1, point2, float(distance)))
                
                for label, height in points_buffer.items():
                    self.matrix[label] = Point(label, height)
                
                for point1, point2, distance in distances_buffer:
                    self.matrix[point1].add_reference(point2, distance)
                    self.matrix[point2].add_reference(point1, distance)
                
                print(f"Matrix loaded from {file_path}")
                logging.info(f"Matrix loaded successfully from {file_path}")
            except Exception as e:
                logging.error(f"Error processing matrix content: {e}")
                print(f"Error processing matrix content: {e}")
            
            self.print_matrix(False)
            Console.wait_for_input()

    def print_points(self, refresh: bool = False):
        if refresh:
            Console.clear_screen()
        Console.print_and_dash("Current Points")
        for point in self.matrix.values():
            if point == list(self.matrix.values())[-1]:
                Console.print_and_dash(str(point))
            else:
                print(str(point))

    def print_distances(self, refresh: bool = False):
        if refresh:
            Console.clear_screen()
        Console.print_and_dash("Current Distances")
        for point in self.matrix.values():
            for distance in point.distances.values():
                print(str(distance))

    def print_matrix(self, refresh: bool = False, tab_size: int = 10):
        if len(self.matrix) == 0:
            print("No points in the matrix.")
        if refresh:
            Console.clear_screen()
        Console.print_and_dash("Current Matrix")
        
        point_labels = list(self.matrix.keys())
        
        # Print point labels and heights in the top row of the table
        header_row = ["heights: "] + [""] + [f"{point}:{self.matrix[point].height}{self.config.current_variables['height_unit']['value']}" for point in point_labels]
        print("\t".join(header_row).expandtabs(tab_size))
        
        # Print distances for each point
        for point1 in point_labels:
            distances_row = [""] + [point1] + [f"{self.matrix[point1].distances[point2].distance}{self.config.current_variables['distance_unit']['value']}" 
                                        if point2 in self.matrix[point1].distances else " " 
                                        for point2 in point_labels]
            print("\t".join(distances_row).expandtabs(tab_size))

        footer_row = ["delta: "] + [""] + [f"{point}:{self.matrix[point].target_thickness}{self.config.current_variables['height_unit']['value']}" for point in point_labels]
        print("\t".join(footer_row).expandtabs(tab_size))

    def delete_points(self):
        while True:
            Console.clear_screen()
            Console.print_and_dash("Delete Points")
            print("Enter the point label to delete, then hit enter.")
            Console.print_and_dash("Hit enter without entering a point to finish deleting points.")
            self.print_matrix(False)
            point_label = input("Enter point label to delete (or press Enter to finish): ").strip()
            if point_label == "":
                if Console.confirm_escape():
                    break
            if point_label in self.matrix:
                del self.matrix[point_label]
                distances = {k: v for k, v in distances.items() if point_label not in k}
                for k in list(distances.keys()):
                    if point_label in k:
                        del distances[k]
                print(f"Point {point_label} deleted.")
            else:
                print(f"Point {point_label} not found.")
            Console.wait_for_input()

    def input_points(self):
        while True:
            Console.clear_screen()
            Console.print_and_dash("Input Points")
            print("Enter the point label, then hit enter.")
            print("You will then be prompted for the height of the point.")
            Console.print_and_dash("Hit enter without entering a point/height to finish inputting points.")
            current_points = ", ".join(f"{key}: {value.height}" for key, value in self.matrix.items())
            print(f"Current points: {current_points}\n")
            
            point_label = Console.validate_input("Enter point label (or press Enter to finish): ", lambda x: x != "", "Invalid point label.")
            if point_label is None:
                break
            elif point_label == "":
                continue
            
            height = Console.validate_input(f"Enter height for point {point_label}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid height. Please enter a number.")
            if height is None:
                break
            
            self.matrix[point_label] = Point(point_label, float(height))
            print(f"Point {point_label} with height {height} added.")

    def input_distances(self):
        while True:
            if len(self.matrix) < 2:
                print("You must have at least 2 points to enter a distance.")
                Console.wait_for_input()
                break
            Console.clear_screen()
            Console.print_and_dash("Input Distances")
            print("Enter the first point, then the second point, then the distance between them.")
            print("You will then be prompted for the distance.")
            print("\nNote: the points must have been entered with their heights before you can enter distances.")
            Console.print_and_dash("Hit enter without entering a point/distance to finish inputting distances.")
            self.print_matrix(False)
            
            point1_label = Console.validate_input("Enter first point (or press Enter to finish): ", self.check_for_points, "Point not found.")
            if point1_label is None:
                break
            elif point1_label == "":
                continue
            
            point2_label = Console.validate_input(f"Enter second point (or press Enter to finish): ", self.check_for_points, "Point not found.")
            if point2_label is None:
                break
            elif point2_label == "":
                continue
            
            distance = Console.validate_input(f"Enter distance between {point1_label} and {point2_label}: ", lambda x: x.replace('.', '', 1).isdigit(), "Invalid distance. Please enter a number.")
            if distance is None:
                break
            elif distance == "":
                continue
            
            self.matrix[point1_label].add_reference(point2_label, float(distance))
            self.matrix[point2_label].add_reference(point1_label, float(distance))
            print(f"Distance between {point1_label} and {point2_label} with distance {distance} added.")

    def check_for_points(self, point_label):
        return point_label in self.matrix