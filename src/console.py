import os
import msvcrt
from .shared_state import SharedState

class Console:
    def __init__(self, action_map, shared_state: SharedState):
        self.action_map = action_map
        self.shared_state = shared_state
        self.current_menu_options = None
        self.current_menu_name = None
        self.current_conditions = None

    def navigate_menu(self, menu_options, menu_name=None, conditions=None):
        self.current_menu_options = menu_options
        self.current_menu_name = menu_name
        self.current_conditions = conditions

        if isinstance(menu_options, list):
            items = menu_options
            title = menu_name if menu_name else "Menu"
        else:
            menu = menu_options[menu_name]
            if conditions is None:
                conditions = {}
            conditions.update({"variables_changed": self.shared_state.variables_changed})
            items = [item for item in menu['items'] if self.evaluate_conditions(item.get('conditions'), conditions)]
            title = menu['title']
        
        index = 0

        def print_items():
            self.clear_screen()
            self.print_and_dash(title)
            for i, item in enumerate(items):
                item_text = item['text']
                if self.shared_state.show_help and 'help_text' in item:
                    item_text += f" : {item['help_text']}"
                if i == index:
                    print(f"> {item_text}")
                else:
                    print(f"  {item_text}")

        def update_items():
            for i, item in enumerate(items):
                item_text = item['text']
                if self.shared_state.show_help and 'help_text' in item:
                    item_text += f" : {item['help_text']}"
                if i == index:
                    print(f"\033[{i+4}H> {item_text}")  # Adjusted cursor position
                else:
                    print(f"\033[{i+4}H  {item_text}")  # Adjusted cursor position
            print("\033[0J", end='')  # Clear from cursor to end of screen

        def move_cursor_up():
            nonlocal index
            while index > 0:
                index -= 1
                if items[index]['action'] != 'none':
                    break

        def move_cursor_down():
            nonlocal index
            while index < len(items) - 1:
                index += 1
                if items[index]['action'] != 'none':
                    break

        print_items()
        while True:
            key = self.get_key_input()
            if key in ['\xe0H', '\x1b[A', 'w']:  # Up arrow or 'w' key
                move_cursor_up()
                update_items()
            elif key in ['\xe0P', '\x1b[B', 's']:  # Down arrow or 's' key
                move_cursor_down()
                update_items()
            elif key == '\r':  # Enter
                selected_item = items[index]
                if selected_item['action'] != 'none':
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
                self.exit_program()
            elif key == '\x1b':  # ESC
                return ''

    def rerender(self):
        if self.current_menu_options is not None:
            self.navigate_menu(self.current_menu_options, self.current_menu_name, self.current_conditions)

    @staticmethod
    def evaluate_conditions(item_conditions, conditions):
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
    def clear_screen():
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