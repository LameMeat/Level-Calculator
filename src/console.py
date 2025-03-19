import os
import msvcrt

class Console:
    @staticmethod
    def print_menu(menu_options, menu_name, menu_callback, menu_data_function=None):
        stay_in_current_menu = True
        while stay_in_current_menu:
            Console.refresh_screen()
            menu = menu_options[menu_name]
            # sort the menu by the keys
            menu = dict(sorted(menu.items()))
            Console.print_and_dash(menu['Title'])
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