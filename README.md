# <a href="https://github.com/vlHan/PassVault"><img src="./demo/logo.png"></a>

[![python](https://img.shields.io/badge/Python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8-blue.svg)](https://www.python.org) [![repo size](https://img.shields.io/github/repo-size/vlHan/PassVault)](#) [![build](https://img.shields.io/badge/build-Passing-green)](#) [![license](https://img.shields.io/github/license/vlHan/PassVault.svg)](LICENSE)

[![asciicast](https://asciinema.org/a/tJaauMOKBy6tp47KSDEQxkm3H.svg)](https://asciinema.org/a/tJaauMOKBy6tp47KSDEQxkm3H)

## What is this? 
Command-line password manager, for educational purposes, that stores localy, in AES encryption, your sensitives datas in a SQLite database (.db). This project was made to learn more about cryptography and **not for intended for actual use**.

## Installation
Clone this repository: `git clone https://github.com/vlHan/PassVault.git` or <a href="https://github.com/vlHan/PassVault/archive/refs/heads/main.zip">download zip</a>
- Enter the folder: `cd PassVault/`
- Install python3 
  - Linux
    - `python3 -m pip install -r requirements.txt`
    - Finished!

  - Windows and macOS
    - [Python 3, download and install](https://www.python.org/downloads/)
    - `python -m pip install -r requirements.txt`
    - Finished!

## Usage
Use the following commands to run the program
```bash
Linux and macOS
  # in the diretory
  $ python3 .
    
  # out of the diretory
  $ python3 PassVault
    
Windows
  # in the diretory
  $ python .
    
  # out of the diretory
  $ python PassVault
```
**⚠️** The program needs all the files, be sure to have all the dependecies and files <a href="https://github.com/vlHan/PassVault#installation">installed</a>.

## How It Works
When running, the program will ask to create a master password. This master password will be encrypted and this key will be used to indenty if the user is actually you, be sure you have saved, because the master password is **unrecoverable**.

### Hash Verification
To authenticate the user, they are prompted to create a master password (that is also used to decrypt data) which is then stored using HMAC autentication code (that use SHA3_512 Hash Function as the digest mod). Whenever the user is prompted to verify their master password, the password they enter is compared to the hash of the stored master password and access if granted if the two hashes match.

```py
try: # try to connect with the database
    self.cursor.execute("SELECT * FROM masterpassword")
    for row in self.cursor.fetchall():
        stored_master = row[0]
        salt = row[1] 

    print("[cyan][PassVault][/cyan] Enter the master password:", end=' ')
    self.master_pw = getpass.getpass("").strip() # ask the master password
    
    # compare the two hashes
    if hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest() == stored_master: 
        # master password is correct

except sqlite3.Error: # if the connection does not work
    # rest of the program
```

### AES Encryption
The encryption method used in this program comes from the python library [PyCryptoDome](https://pypi.org/project/pycryptodome/). This program uses AES encryption methods to store sensitive data (in this case passwords) into a SQLite database.

### SQLite Functions
The SQLite database is used to store sensitive data, as mentioned above. This type of database was used instead of MySQL, as it is easily transported and lightweight. Despite being less secure, it can be easily used and manipulated, so it is possible to keep it in a backup, in case the database is localy lost, you only need the password manager to be able to decrypt the passwords stored in your backup database.

## Contributors
See also the list of contributors who participated in this project.

- **[vlHan](https://github.com/vlHan)** - *Initial work* 
- **[carvalinh0](https://github.com/carvalinh0)** - *AES encryption* 

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

## License 
This project is licensed under the MIT License - see the [LICENSE](https://github.com/vlHan/PassVault/blob/master/LICENSE) file for details

[⬆ Back to top](https://github.com/vlHan/PassVault#)<br>
