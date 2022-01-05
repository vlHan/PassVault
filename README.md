# <a href="https://github.com/vlHan/PassVault"><img src="./demo/logo.png"></a>

<p>
   <img alt="Languages" src="https://img.shields.io/badge/Python-3.7%20%7C%203.8-blue.svg"> 
   <img alt="Repository size" src="https://img.shields.io/github/repo-size/vlHan/PassVault">
   <img alt="License" src="https://img.shields.io/github/license/vlHan/PassVault.svg">
</p>

It is a command-line password manager, for educational purposes, that stores localy, in AES encryption, your sensitives datas in a SQlite database (.db). This project was made to learn more about cryptography and **not for intended for actual use**. This software is used at your own risks. It is provided as is and I (including any contributors) do not take any responsibility for any damage or loss done with or by it.


## Installation
Clone this repository: `git clone https://github.com/vlHan/PassVault` or <a href="https://github.com/vlHan/PassVault/archive/refs/heads/main.zip">download zip</a>
- Enter the folder: `cd PassVault/`
- Install python3 
  - Linux
    - `sudo apt-get install python3`
    - `chmod +x *`
    - `python3 -m pip install -r requirements.txt`
    - Finished!

  - Windows and Mac
    - [Python 3, download and install](https://www.python.org/downloads/)
    - `python -m pip install -r requirements.txt`
    - Finished!

## Usage
```bash
# Install the dependecies 
$ pip3 install -r requirements.txt

# If you are in the diretory 
$ python3 .

# If you are not
$ python3 PassVault
```
**⚠️** The program needs all the files, be sure to have all the dependecies and files installed.

## How It Works

1. After running you need to create your master password. This master password will be encrypted and this key will be used to indenty if the user is actually you, be sure you have saved, because the master password is **unrecoverable**.
2. Follow the steps and answer the inputs, these informations will be saved. 

After following the steps, the code will store your datas, encrypted in AES encryption, that comes from a python library [pycryptodome](https://pypi.org/project/pycryptodome/), in a SQlite file. To authenticate the user, they are prompted to create a master password (that is also used to decrypt data) which is then stored using HMAC autentication code (that use SHA3_512 Hash Function for the digest mod). Whenever the user is prompted to verify their master password, the password they enter is compared to the hash of the stored master password and access if granted if the two hashes match.

```py
if os.path.isfile('vault.db'): # verify if the database exist
      cursor.execute("SELECT * FROM masterpassword") # select the stored data 
      for row in cursor.fetchall(): 
          master = row[0] 
          salt = row[1] 
      
      self.master_pw = getpass.getpass('Enter your master password: ') # ask the master password
      h = hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest() # use HMAC and encrypt in sha3_512 HASH Function

      # compare the hashes
      if h == master:
        # rest of the program
```

## Technologies 
This project was developed with the following technologies:

- UI:
  - <a href="https://pypi.org/project/colorama/">colorama</a> (add color in the terminal)
- Database:
  - <a href="https://docs.python.org/3/library/sqlite3.html">db-sqlite3</a> (sqlite library)
- Encryption: 
  - <a href="https://pypi.org/project/pycryptodome/">pycryptodome</a> (AES cryptography) 
  - <a href="https://docs.python.org/3/library/hmac.html">hmac</a> (Keyed-Hashing for Message Authentication)
  - <a href="https://docs.python.org/3/library/hashlib.html">hashlib</a> (hash function to use sha3_512)
  - <a href="https://docs.python.org/3/library/base64.html">base64</a> 
  - <a href="https://docs.python.org/3/library/random.html">random</a> and <a href="https://docs.python.org/pt-br/3/library/string.html">string</a> (generate random string)
- Outro:
  - <a href="https://pypi.org/project/requests/">requests</a> (send HTTP request to the URL gaved)
  - <a href="https://docs.python.org/3/library/os.html">os</a> and <a href="https://docs.python.org/3/library/sys.html">sys</a> (system libraries)
  - <a href="https://docs.python.org/pt-br/3/library/getpass.html">getpass</a> (input)
  - <a href="https://docs.python.org/3/library/time.html">time</a> (interval using sleep)

## Example
<img src="./demo/demo.gif" height="50%" width="100%"><br>

## Contributing
If you want to contribute see [guidelines for contributing](CONTRIBUTING.md).

### Shoutouts
- @carvalinh0 for helping me in the AES encryption.

| [<img src="https://github.com/vlHan.png" width="115"><br><small>@vlHan</small>](https://github.com/vlHan) | [<img src="https://github.com/carvalinh0.png" width="115"><br><small>@carvalinh0</small>](https://github.com/carvalinh0) 
| :---: | :---: | 

## License 
This project is under the [MIT License](LICENSE).
