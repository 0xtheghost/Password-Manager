import json
import os
import bcrypt
from cryptography.fernet import Fernet
from collections import OrderedDict
from colorama import Fore

class PasswordManager:
    def __init__(self, key_file="key.key", encrypted_file='data.enc', password_file='password.hash') -> None:
        self.key_file = key_file
        self.encrypted_file = encrypted_file
        self.password_file = password_file
        self.cipher = None

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as file:
            file.write(key)
        print(Fore.BLUE + f"New key generated and saved in :\n{Fore.GREEN}'{self.key_file}'{Fore.RESET}")
        self.cipher = Fernet(key)

    def load_key(self):
        try:
            with open(self.key_file, 'rb') as file:
                key = file.read()
                self.cipher = Fernet(key)
                print(Fore.CYAN+f"[Key loaded from : {Fore.GREEN}'{self.key_file}'{Fore.CYAN}]{Fore.RESET}")
        except FileNotFoundError:
            print(Fore.RED+f"Keyfile not found{Fore.RESET}")
            choice = input(Fore.CYAN+f"Do you want to generate a new key? (y/n) : {Fore.GREEN}"+Fore.RESET)
            if choice.lower() == 'y':
                self.generate_key()
            else:
                print(Fore.RED+"As no key has been loaded, operations requiring a key will not be possible."+Fore.RESET)
    
    def set_password(self):
        password = input(Fore.BLUE+"Enter new master password : "+Fore.RESET).encode()
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        with open(self.password_file, 'wb') as file:
            file.write(hashed)
        print(Fore.GREEN+"Master password set successfully."+Fore.RESET)

    def verify_password(self):
        """Verifies if the master password is correct."""
        if not os.path.exists(self.password_file):
            print(Fore.YELLOW+"No master password found. Please create one."+Fore.RESET)
            self.set_password()
        
        password = input(Fore.BLUE+"Enter master password : "+Fore.RESET).encode()
        with open(self.password_file, 'rb') as file:
            hashed = file.read()

        if bcrypt.checkpw(password, hashed):
            print(Fore.GREEN+"Authentication successful."+Fore.RESET)
            return True
        else:
            print(Fore.RED+"Authentication failed. Incorrect password."+Fore.RESET)
            return False
        
    def change_key(self):
        if os.path.exists(self.encrypted_file):
            current_data = self.load_data() or {}
        else:
            current_data = {}

        self.generate_key()

        if current_data:
            self.save_data(current_data)
            print(Fore.GREEN+"Data re-encrypted with the new key.\n"+Fore.RESET)
        else:
            print(Fore.RED+"No data found to re-encrypt."+Fore.RESET)

        input(Fore.MAGENTA+"\nPress enter to finish ")

    def save_data(self, data):
        if self.cipher is None:
            raise ValueError(Fore.RED+"Encryptor not initialized. Load or generate a key."+Fore.RESET)
        
        json_data = json.dumps(data, ensure_ascii=False).encode()
        encrypted_data = self.cipher.encrypt(json_data)

        with open(self.encrypted_file, 'wb') as file:
            file.write(encrypted_data)
        print(Fore.BLUE+f"Encrypted data saved in : {Fore.GREEN}'{self.encrypted_file}'{Fore.RESET}")

    def load_data(self):
        if self.cipher is None:
            raise ValueError(Fore.RED+"Encryptor not initialized. Load or generate a key."+Fore.RESET)
        
        try:
            with open(self.encrypted_file, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = self.cipher.decrypt(encrypted_data).decode()
                data = json.loads(decrypted_data)
                print(Fore.BLUE+f"Data decrypted from : {Fore.GREEN}'{self.encrypted_file}'{Fore.RESET}")
                return data
        except FileNotFoundError:
            print(Fore.RED+f"Data file not found :\n'{self.encrypted_file}'{Fore.RESET}")
            return None

    def load_json_file(self, json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(Fore.CYAN+f"Data loaded from : {Fore.GREEN}'{json_file}'{Fore.RESET}")
                return data
        except FileNotFoundError:
            print(Fore.RED+f"Data file not found :\n'{self.encrypted_file}'{Fore.RESET}")
            return None

    def import_json(self, json_file):
        data = self.load_json_file(json_file)
        if data:
            current_data = self.load_data() or {}
            current_data.update(data)
            self.save_data(current_data)

    def export_json(self, json_file):
        data = self.load_data()
        if data:
            with open(json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(Fore.CYAN+f"Data exported to {Fore.GREEN}'{json_file}'{Fore.CYAN} successfully.{Fore.RESET}")  

    def add_or_update_data_at_path(self, path, value):
        data = self.load_data() or {}
        parent, final_key = self.navigate_to_path(data, path)
        parent[final_key] = str(value)
        print(Fore.CYAN+f"Add/update data at location {Fore.GREEN}'{path}'{Fore.CYAN} : {value}"+Fore.RESET)
        self.save_data(data)

    def delete_data_at_path(self, path):
        data = self.load_data()
        if data is None:
            print(Fore.RED+"The data doesn't exist."+Fore.RESET)
            return

        parent, final_key = self.navigate_to_path(data, path)
        if final_key in parent:
            del parent[final_key]
            print(Fore.MAGENTA+f"Data deleted in {Fore.GREEN}'{path}'{Fore.RESET}")
            self.save_data(data)
        else:
            print(Fore.RED+f"The key {Fore.MAGENTA}'{final_key}'{Fore.RED} does not exist at the specified location."+Fore.RESET)

    def show_data_at_path(self, path=None):
        data = self.load_data()
        if data:
            if path:
                parent, final_key = self.navigate_to_path(data, path)
                if final_key in parent:
                    print(Fore.BLUE+f"Location data '{path}' : {Fore.GREEN}\n{json.dumps(parent[final_key], indent=4, ensure_ascii=False)}"+Fore.RESET)
                    input(Fore.MAGENTA+"Press enter to finish")
                else:
                    print(Fore.RED+f"The key {Fore.MAGENTA}'{final_key}'{Fore.RED} does not exist at the specified location."+Fore.RESET)
            else:
                print(Fore.BLUE+f"\nCurrent data : {Fore.GREEN}\n{json.dumps(data, indent=4, ensure_ascii=False)}\n"+Fore.RESET)
                input(Fore.MAGENTA+"Press enter to finish ")
        else:
            print("No data available.")

    def navigate_to_path(self, data, path):
        keys = path.split('/')
        parent = data
        for key in keys[:-1]:
            if key not in parent:
                parent[key] = {}
            parent = parent[key]
        return parent, keys[-1]

    def run_cli(self):
        if not self.verify_password():
            return
        
        while True:
            os.system("cls")
            print(Fore.CYAN + """\n
███╗   ███╗ █████╗ ██╗███╗   ██╗    ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
████╗ ████║██╔══██╗██║████╗  ██║    ████╗ ████║██╔════╝████╗  ██║██║   ██║
██╔████╔██║███████║██║██╔██╗ ██║    ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝                                                           
            """+ Fore.RESET)
            manager.load_key()
            print(Fore.MAGENTA+"\n====================================="+Fore.RESET)
            print(Fore.GREEN + f"[1] - {Fore.CYAN}Show data"+Fore.RESET)
            print(Fore.GREEN + f"[2] - {Fore.CYAN}Add/Update data"+Fore.RESET)
            print(Fore.GREEN + f"[3] - {Fore.CYAN}Delete data"+Fore.RESET)
            print(Fore.GREEN + f"[4] - {Fore.CYAN}Change key"+Fore.RESET)
            print(Fore.GREEN + f"[5] - {Fore.CYAN}Export .json"+Fore.RESET)
            print(Fore.GREEN + f"[6] - {Fore.CYAN}Import .json"+Fore.RESET)
            print(Fore.GREEN + f"[7] - {Fore.CYAN}Quit"+Fore.RESET)
            print(Fore.MAGENTA+"=====================================\n"+Fore.RESET)
            choice = input(Fore.CYAN+"Choose an option : "+Fore.RESET)
            if choice == '1':
                path = input(Fore.BLUE+"Enter the location path (leave empty for root): " + Fore.RESET)
                os.system("cls")
                self.show_data_at_path(path)
            elif choice == '2':
                path = input(Fore.BLUE + "Enter the location path: " + Fore.RESET)
                value = input(Fore.BLUE + "Enter the value: " + Fore.RESET)
                os.system("cls")
                self.add_or_update_data_at_path(path, value)
            elif choice == '3':
                path = input(Fore.RED + "Enter the location path: " + Fore.RESET)
                os.system("cls")
                self.delete_data_at_path(path)
            elif choice == '4':
                self.change_key()
            elif choice == '5':
                json_file = input(Fore.CYAN + "Enter the JSON file to export to: " + Fore.RESET)
                os.system("cls")
                self.export_json(json_file)
            elif choice == '6':
                json_file = input(Fore.CYAN + "Enter the JSON file to import from: " + Fore.RESET)
                os.system("cls")
                self.import_json(json_file)
            elif choice == '7':
                os.system("cls")
                print(Fore.MAGENTA+"""
 ██████╗  ██████╗  ██████╗ ██████╗ ██████╗ ██╗   ██╗███████╗██╗
██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██║
██║  ███╗██║   ██║██║   ██║██║  ██║██████╔╝ ╚████╔╝ █████╗  ██║
██║   ██║██║   ██║██║   ██║██║  ██║██╔══██╗  ╚██╔╝  ██╔══╝  ╚═╝
╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║   ███████╗██╗
 ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝"""+Fore.RESET)
                break
            else:
                print(Fore.RED+"Invalid option."+Fore.RESET)

if __name__ == "__main__":
    manager = PasswordManager()
    manager.run_cli()