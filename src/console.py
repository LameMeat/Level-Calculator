import os
import msvcrt
from .shared_state import SharedState

class Console:
    def __init__(self, action_map, shared_state: SharedState):
        self.action_map = action_map
        self.shared_state = shared_state

    def navigate_menu(self, menu_options, menu_name=None, conditions=None):
        if isinstance(menu_options, list):
            items = menu_options
            title = menu_name if menu_name else "Menu"
        else:
            menu = menu_options[menu_name]
            if conditions is None:
                conditions = {}
            conditions.update({"variables_changed": self.shared_state.variables_changed})
            items = [item['text'] for item in menu['items'] if self.evaluate_conditions(item.get('conditions'), conditions)]
            title = menu['title']
        
        index = 0

        def print_items():
            self.refresh_screen()
            self.print_and_dash(title)
            print(f"shared_state.variables_changed: {self.shared_state.variables_changed}")
            for i, item in enumerate(items):
                if i == index:
                    print(f"> {item}")
                else:
                    print(f"  {item}")

        def update_items():
            for i, item in enumerate(items):
                if i == index:
                    print(f"\033[{i+5}H> {item}")  # Adjusted cursor position
                else:
                    print(f"\033[{i+5}H  {item}")  # Adjusted cursor position
            print("\033[0J", end='')  # Clear from cursor to end of screen

        print_items()
        while True:
            key = self.get_key_input()
            if key in ['\xe0H', '\x1b[A', 'w']:  # Up arrow or 'w' key
                if index > 0:
                    index -= 1
                    update_items()
            elif key in ['\xe0P', '\x1b[B', 's']:  # Down arrow or 's' key
                if index < len(items) - 1:
                    index += 1
                    update_items()
            elif key == '\r':  # Enter
                if isinstance(menu_options, list):
                    selected_item = items[index]
                    print(f"Selected: {selected_item}")
                    self.wait_for_input()
                    return selected_item
                else:
                    selected_item = menu['items'][index]
                    action = selected_item['action']
                    if action in self.action_map:
                        result = self.action_map[action]()
                        if result is False:
                            break
                    else:
                        print("Invalid choice, please try again.")
                        self.wait_for_input()
                    print_items()
            elif key == '\x03':  # Ctrl+C
                return ''

    @staticmethod
    def evaluate_conditions(item_conditions, conditions):
        print(item_conditions, conditions)
        if not item_conditions or not conditions:
            return True
        if conditions.get(item_conditions['condition']) != item_conditions['value']:
            return False
        return True

    @staticmethod
    def get_key_input():
        key = msvcrt.getch()
        if key in [b'\xe0', b'\x00']:  # Special keys (arrows, f keys, ins, del, etc.) on Windows
            key += msvcrt.getch()  # Get the second byte
        elif key == b'\x1b':  # ESC key (start of arrow keys on Linux)
            key += msvcrt.getch() + msvcrt.getch()  # Get the next two bytes
        return key.decode('utf-8', errors='ignore')

    @staticmethod
    def validate_input(prompt, validation_func, error_message):
        while True:
            user_input = input(prompt).strip()
            if user_input == "":
                if Console.confirm_escape():
                    return None
                else:
                    return ""
            if validation_func(user_input):
                return user_input
            else:
                print(error_message)
                Console.wait_for_input()

    @staticmethod
    def refresh_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_and_dash(string):
        print(string)
        print("-" * len(string), "\n")

    @staticmethod
    def wait_for_input():
        input("Press Enter to continue...")

    @staticmethod
    def confirm_escape():
        print("Hit enter again to confirm escape, or type anything else to remain")
        key = msvcrt.getch()
        if key == b'\r':  # Enter key
            return True
        else:
            return False
        
    @staticmethod
    def exit_program():
        print("Exiting...")
        os._exit(0)