from .console import Console
import os
import json

class FileManager:
    def __init__(self, console: Console):
        self.console = console

    def prompt_for_file_choice(self, directory, refresh: bool = False):
        if refresh:
            self.console.refresh_screen()
        files = self.list_files(directory)
        print(files)
        return self.console.navigate_menu(files, "Load File")

    @staticmethod
    def load_file(file_path):
        if not os.path.isfile(file_path):
            print(f"File {file_path} not found.")
            return None
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return None

    @staticmethod
    def save_file(file_path, content):
        if os.path.isfile(file_path):
            overwrite = FileManager.prompt_for_overwrite()
            if overwrite.lower() != 'y':
                print("Save operation cancelled.")
                return
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            print(f"File saved to {file_path}.")
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")

    @staticmethod
    def delete_file(file_path):
        if not os.path.isfile(file_path):
            print(f"File {file_path} not found.")
            return
        try:
            os.remove(file_path)
            print(f"File {file_path} deleted.")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    @staticmethod
    def list_files(directory, extension=None):
        print(f"Listing files in directory: {directory}")
        if not os.path.isdir(directory):
            print(f"Directory {directory} not found.")
            return []
        try:
            if extension:
                return [f for f in os.listdir(directory) if f.endswith(extension)]
            return os.listdir(directory)
        except Exception as e:
            print(f"Error listing files in directory {directory}: {e}")
            return []

    @staticmethod
    def ensure_directory_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def prompt_for_save_name():
        return Console.validate_input("Enter the name of the backup: ", lambda x: x != "", "Name cannot be empty.")
    
    @staticmethod
    def prompt_for_save_location():
        return Console.validate_input("Enter the save location: ", lambda x: x != "", "Location cannot be empty.")
    
    @staticmethod
    def prompt_for_overwrite():
        return input("File already exists. Overwrite? (y/n): ").strip()

    def save_with_prompts(self, content):
        save_location = self.prompt_for_save_location()
        save_name = self.prompt_for_save_name()
        file_path = os.path.join(save_location, save_name)
        
        if os.path.isfile(file_path):
            overwrite = self.prompt_for_overwrite()
            if overwrite.lower() != 'y':
                print("Save operation cancelled.")
                return
        
        self.save_file(file_path, content)

    @staticmethod
    def load_json(file_path):
        if not os.path.isfile(file_path):
            print(f"File {file_path} not found.")
            return None
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {e}")
            return None