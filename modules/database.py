# -*- coding: utf-8 -*-
import random
import sqlite3
import string
import time
import os
import sys
import json

from modules.banner import *
from modules.exceptions import *
from modules.menu import *

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

__author__ = "vlHan"
__version__ = "V1.0"


class DataBase:
    def __init__(self, master_pssw: str) -> None:
        """
        Argument
            - master_pssw [str] = the master password

        Variables
            - platform [str] = the platform
            - mail [str] = email
            - pw [str] = password that will be stored in the database.
            - url [str] = url from the platform

        """
        self.master_pssw = master_pssw
        self.datab = sqlite3.connect("db/data.db")
        self.cursor = self.datab.cursor()
        try:
            # Connect with the SQlite and create the table.
            self.cursor.execute(
                "CREATE TABLE passwords (platform txt, email txt, password txt, url txt, key txt)")
            self.datab.commit()
            self.datab.close()
        except sqlite3.Error:
            pass

    def data_encrypt(self, pssw: str, key: str):
        """
        Encrypt and save the data to a file using master password as the key
            AES, base64

        Arguments
            - data [str]
            - key [str]

        Variables 
            - cipher = cipher is the initialization vector to use for encryption or decryption
            - concatenate_bytes = returns the cypher text
        """
        if not pssw:
            raise EmptyInput
        pssw = pssw.encode('utf-8')
        key = key.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC)
        concatenate_bytes = cipher.encrypt(pad(pssw, AES.block_size))

        # pass the initial_value to base64
        iv = b64encode(cipher.iv).decode('utf-8')

        concatenate = b64encode(concatenate_bytes).decode(
            'utf-8')  # cyphertext to base64

        return (iv, concatenate)

    def data_decrypt(self, initial_value: str, ciphertext: str, key: str):
        """
        Decryption part
            AES, base64

        Arguments
            - initial_value [str]
            - ciphertext [str]
            - key [str]

        Returns 
            - pt [str]
        """

        initial_value = b64decode(initial_value)
        concatenate = b64decode(ciphertext)

        key = key.encode('utf-8')

        # return the initial_value text
        cipher = AES.new(key, AES.MODE_CBC, initial_value)
        # try decrypt the cypher text

        pt = unpad(cipher.decrypt(concatenate), AES.block_size)

        return pt

    def save_password(self, platform: str, mail: str, password: str, url: str) -> None:
        """
        Add values in the Data Base SQlite.

        Arguments
            - platform [str]
            - mail [str]
            - password [str]
            - url [str]

        Returns 
            The password saved in the database 

        """
        if os.path.isfile("db/info.json"):
            with open("db/info.json", 'r') as f:
                jfile = json.load(f)

            self.master_pssw = self.master_pssw + \
                jfile["Informations"]["salt"]

            infos = []
            stored_infos = [platform, mail, password, url]
            for i in stored_infos:
                try:
                    _iv, _ct = self.data_encrypt(i, self.master_pssw[0:32])
                except EmptyInput:
                    sys.exit(Fore.RED + 'The input cannot be empty. Please try again.' + Style.RESET_ALL)
                concatenate = _iv + "|" + _ct
                infos.append(concatenate)

            stored_key = self.cursor.execute('SELECT key FROM passwords')
            while True:
                key = "".join(random.choice(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(4))
                if key not in stored_key:
                    break

            self.cursor.execute(f"INSERT INTO passwords VALUES('{infos[0]}', '{infos[1]}', '{infos[2]}', '{infos[3]}', '{key}')")
            self.datab.commit()
            self.datab.close()
            print(
                Fore.GREEN + "\nThank you! Datas were added successfully.\n" + Style.RESET_ALL)

    def __edit_password(self, option: str, new: str, key: str) -> None:
        """
        Update values in the database SQlite.

        Returns
            [str] the new password changed in the database
        """
        if os.path.isfile('db/info.json'):
            try:
                with open("db/info.json", 'r') as f:
                    jfile = json.load(f)
                self.master_pssw = self.master_pssw + \
                    jfile["Informations"]["salt"]

            except KeyError:
                raise PasswordNotFound

            _iv, _ct = self.data_encrypt(
                new, self.master_pssw[0:32])
            ct_new_mail = _iv + "|" + _ct
            self.cursor.execute(
                f"UPDATE passwords SET {option} = '{ct_new_mail}' WHERE key = '{key}'")
            print(
                Fore.GREEN + f"The {option} has successfully changed to {new}." + Style.RESET_ALL)
            self.datab.commit()
            self.datab.close()

        else:
            raise DatabaseNotFound

    def see_all(self) -> None:
        """
        See all passwords stored in the database.

        Returns
            - [tuple] The passwords stored

        Raises
            DatabaseEmpty: the database is empty
        """

        self.cursor.execute("""SELECT COUNT(*) from passwords""")
        result = self.cursor.fetchall()

        if result[0][0] == 0:
            # verify if the database is empty - cannot opperate in a empty database
            raise DatabaseEmpty

        else:
            print()
            if os.path.isfile("db/info.json"):
                try:
                    with open("db/info.json", 'r') as f:
                        # Open the information file
                        jfile = json.load(f)

                    self.master_pssw = self.master_pssw + \
                        jfile["Informations"]["salt"]

                except KeyError:
                    raise PasswordNotFound

                infos = []
                for row in self.cursor.execute('SELECT * FROM passwords'):
                    infos.append(row[0])
                    infos.append(row[1])
                    infos.append(row[2])
                    infos.append(row[3])
                    decrypted = []
                    for i in infos:
                        decrypted.append(self.data_decrypt(str(i).split("|")[0], str(i).split("|")[1], self.master_pssw[0:32]))
                    infos = []

                    print(f"Platform: {decrypted[0].decode()}\nEmail: {decrypted[1].decode()}\nPassword: {decrypted[2].decode()}\nURL: {decrypted[3].decode()}\nKey: {str(row[4])}\n")

            else:
                raise DatabaseNotFound

    def delete_one(self, key: str) -> None:
        """
        Delete values in the Data Base SQlite.

        Arguments
            - key [str]
        """
        self.cursor.execute(
            f"DELETE from passwords WHERE key = '{key}'")
        self.datab.commit()
        print(Fore.GREEN +
              "\nThe password was deleted successfully.\n" + Style.RESET_ALL)
        self.cursor.execute("SELECT * from passwords")

        try:
            self.see_all()
        except DatabaseEmpty:
            print("\nThe database is empty. Try adding a password.")

        self.datab.commit()
        self.datab.close()

    def delete_pwds(self) -> None:
        """
        Delete all passwords stored in the database 
        (Normal passwords not the master)

        Returns
            DataBase empty (SQlite)

        Raises 
            Database
        """
        self.cursor.execute("""SELECT COUNT(*) from passwords""")
        result = self.cursor.fetchall()

        # verify if the database is empty - cannot opperate in a empty database
        if result[0][0] == 0:
            raise DatabaseEmpty

        else:
            print(Fore.RED +
                  "Deleting all data... (database)" + Style.RESET_ALL)
            print("Removing...")
            time.sleep(2)

            # Dropping the databale
            self.cursor.execute("DROP TABLE passwords")

            self.datab.commit()
            self.datab.close()

            time.sleep(1)
            print(
                Fore.GREEN + "Done. All the passwords stored had been deleted with success." + Style.RESET_ALL)

    def delete_master(self):
        """Delete the master password and all the informations. It 
        is not possible decrypt the data without the master password.

        Returns 
            The master password deleted (.json)
            The database SQlite empty (.db)

        Raises 
            sqlite3.Error: error in the database  
            DatabaseNotFound: database was not found 

        """
        if os.path.isfile('db/info.json') and os.path.isfile('db/data.db'):
            print(Fore.RED + "Deleting all the passwords..." + Style.RESET_ALL)
            time.sleep(2)
            try:
                print("Removing...")
                os.remove('db/info.json')

                self.cursor.execute("""SELECT COUNT(*) from passwords""")
                self.cursor.execute("DROP TABLE passwords")
                self.datab.commit()
                self.datab.close()

            except sqlite3.Error:
                raise sqlite3.Error

            time.sleep(1)

            print(Fore.GREEN + "Done. All the passwods including the master password had been deleted with success." + Style.RESET_ALL)
            time.sleep(1)

            print(Fore.RED + 'Now you will be logged out.' + Style.RESET_ALL)
            time.sleep(2)

            banner()
            sys.exit(Fore.GREEN + 'Thanks for using.' + Style.RESET_ALL)

        else:
            raise DatabaseNotFound
