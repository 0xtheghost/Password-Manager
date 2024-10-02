# Password-Manager by 0xtheghost
## Table of Contents

- [About](#About)
- [Features](#Features)
- [Setup Installation](#SetupInstallation)
- [Usage](#Usage)
- [License](#License)

## About

**Password-Manager** is a command-line interface (CLI) Password Manager that securely stores and manages passwords using encryption techniques. It utilizes `bcrypt` for hashing and verifying the master password, and `cryptography.fernet` for encrypting and decrypting data. It allows users to add, view, update, delete, and manage sensitive information, protected by a master password.

The program provides an interactive interface for managing sensitive information, stored in an encrypted file, with features such as key generation, password management, and JSON import/export.

## Features

- Master Password Protection: Secure your data with a hashed master password.
- Encryption/Decryption: Uses Fernet encryption to secure sensitive data.
- Key Management: Generate, load, and change encryption keys.
- Data Management:
    - Add or update data entries.
    - View specific data entries or the entire dataset.
    - Delete data entries.
- Import/Export: Import and export data as JSON files.
- Interactive CLI: Provides a simple menu-driven interface for managing data.

## SetupInstallation
1. Clone the repository:
``` bash
git clone https://github.com/0xtheghost/Password-Manager.git
cd Password-Manager
```
2. Install the required dependencies:
``` bash
pip install -r requirements.txt
```
3. Run the application :
``` bash
python main.py
```

## Usage

Upon starting the application, you will be prompted to enter the master password. If none exists, the program will guide you to set one.

### Menu Options:
1. Show Data: View all stored data or data at a specific path.
2. Add/Update Data: Add new data or update existing data at a given path.
3. Delete Data: Remove data from a specified path.
4. Change Key: Generate a new encryption key and re-encrypt the data.
5. Export to JSON: Save your data into a JSON file.
6. Import from JSON: Load data from an existing JSON file and merge it with the current data.
7. Quit: Exit the application.
### How It Works
- **Encryption Key:** Stored in a file (`key.key`), used to encrypt and decrypt your data.
- **Data Storage:** Encrypted data is saved in `data.enc`. The content is a JSON structure that holds key-value pairs.
- **Master Password:** The master password is hashed and stored in `password.hash` using bcrypt. It must be provided to unlock the manager and perform actions.
### Security Considerations
- **Key Management:** The key file is crucial for decrypting your data. Do not lose it, or you will lose access to your stored information.
- **Password Security:** The master password is hashed using bcrypt. However, make sure to choose a strong password to prevent brute-force attacks.
### Example
Here’s a quick example of how to add, view, and update data:
1. Start the program and authenticate with your master password.
2. Select option `2` to add or update data.
3. Provide a location path (e.g., `accounts/github`) and enter the value (e.g., `my-github-password`).
4. To view the added data, select option `1` and input the same path (`accounts/github`).

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/0xtheghost/Password-Manager/blob/main/LICENSE) file for details.