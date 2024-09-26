import json
from cryptography.fernet import Fernet
from collections import OrderedDict

class PasswordManager:
    def __init__(self, key_file="key.key", encrypted_file='data.enc') -> None:
        self.key_file = key_file
        self.encrypted_file = encrypted_file
        self.cipher = None
        self.load_key()

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as file:
            file.write(key)
        print(f"Nouvelle clé générée et sauvegardée dans {self.key_file}")
        self.cipher = Fernet(key)

    def load_key(self):
        try:
            with open(self.key_file, 'rb') as file:
                key = file.read()
                self.cipher = Fernet(key)
                print(f"Clé chargée depuis {self.key_file}")
        except FileNotFoundError:
            print(f"Fichier de clé non trouvé : {self.key_file}.")
            choice = input("Voulez-vous générer une nouvelle clé ? (o/n) : ")
            if choice.lower() == 'o':
                self.generate_key()
            else:
                print("Aucune clé n'a été chargée, les opérations nécessitant une clé ne seront pas possibles.")

    def save_data(self, data):
        if self.cipher is None:
            raise ValueError("Le chiffreur n'est pas initialisé. Chargez ou générez une clé.")
        
        json_data = json.dumps(data, ensure_ascii=False).encode()
        encrypted_data = self.cipher.encrypt(json_data)

        with open(self.encrypted_file, 'wb') as file:
            file.write(encrypted_data)
        print(f"Données chiffrées sauvegardées dans {self.encrypted_file}")

    def load_data(self):
        if self.cipher is None:
            raise ValueError("Le chiffreur n'est pas initialisé. Chargez ou générez une clé.")
        
        try:
            with open(self.encrypted_file, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = self.cipher.decrypt(encrypted_data).decode()
                data = json.loads(decrypted_data)
                print(f"Données déchiffrées depuis {self.encrypted_file}")
                return data
        except FileNotFoundError:
            print(f"Fichier de données non trouvé : {self.encrypted_file}")
            return None

    def load_json_file(self, json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"Données chargées depuis {json_file}")
                return data
        except FileNotFoundError:
            print(f"Fichier JSON non trouvé : {json_file}")
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
            print(f"Données exportées vers {json_file} avec succès.")

    def add_or_update_data_at_path(self, path, value):
        data = self.load_data() or {}
        parent, final_key = self.navigate_to_path(data, path)
        parent[final_key] = value
        print(f"Ajout/Mise à jour de la donnée à l'emplacement '{path}' : {value}")
        self.save_data(data)

    def delete_data_at_path(self, path):
        data = self.load_data()
        if data is None:
            print("Les données n'existent pas.")
            return

        parent, final_key = self.navigate_to_path(data, path)
        if final_key in parent:
            del parent[final_key]
            print(f"Donnée supprimée à l'emplacement '{path}'")
            self.save_data(data)
        else:
            print(f"La clé '{final_key}' n'existe pas à l'emplacement spécifié.")

    def show_data_at_path(self, path=None):
        data = self.load_data()
        if data:
            if path:
                parent, final_key = self.navigate_to_path(data, path)
                if final_key in parent:
                    print(f"Donnée à l'emplacement '{path}' : {parent[final_key]}")
                else:
                    print(f"La clé '{final_key}' n'existe pas à l'emplacement spécifié.")
            else:
                print("Données actuelles :")
                print(json.dumps(data, indent=4, ensure_ascii=False))
        else:
            print("Aucune donnée disponible.")

    def navigate_to_path(self, data, path):
        keys = path.split('/')
        parent = data
        for key in keys[:-1]:
            if key not in parent:
                parent[key] = {}
            parent = parent[key]
        return parent, keys[-1]

    def run_cli(self):
        """Exécute le système de navigation des données via la CLI."""
        while True:
            print("\n=== Menu Principal ===")
            print("1. Ajouter ou mettre à jour une donnée")
            print("2. Supprimer une donnée")
            print("3. Afficher des données")
            print("4. Importer des données depuis un fichier JSON")
            print("5. Exporter les données vers un fichier JSON")
            print("6. Quitter")

            choice = input("Choisissez une option (1-6) : ")
            if choice == '1':
                path = input("Entrez le chemin (ex: email1/google) : ")
                value = input("Entrez la valeur : ")
                self.add_or_update_data_at_path(path, value)
            elif choice == '2':
                path = input("Entrez le chemin à supprimer (ex: email1/google) : ")
                self.delete_data_at_path(path)
            elif choice == '3':
                path = input("Entrez le chemin à afficher (laisser vide pour tout afficher) : ")
                self.show_data_at_path(path.strip() or None)
            elif choice == '4':
                json_file = input("Entrez le chemin du fichier JSON à importer : ")
                self.import_json(json_file)
            elif choice == '5':
                json_file = input("Entrez le chemin du fichier JSON pour l'exportation : ")
                self.export_json(json_file)
            elif choice == '6':
                print("Au revoir!")
                break
            else:
                print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    manager = PasswordManager()
    manager.run_cli()
