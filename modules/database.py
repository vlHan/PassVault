# -*- coding: utf-8 -*-
from modules import *
import sqlite3
import time
import os
import sys
from colorama import Fore, Style 

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class DataBase:
    def __init__(self, master_pssw: str) -> None:
        """
        Function to store the data in the database.

        Argument
            - master_pssw [str] = the master password

        """
        self.master_pssw = master_pssw
        self.datab = sqlite3.connect("vault.db")
        self.cursor = self.datab.cursor()
        # Connect with the SQlite and create the table.
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                platform TEXT NOT NULL,
                email TEXT NOT NULL, 
                password TEXT NOT NULL, 
                url TEXT NOT NULL
            );"""
        )
        self.cursor.execute("""SELECT * FROM masterpassword""")
        for row in self.cursor.fetchall():
            self.salt = row[1] 


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

        concatenate = b64encode(concatenate_bytes).decode('utf-8')  # cyphertext to base64

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

        Returns 
            The password saved in the database 

        """
        if os.path.isfile("vault.db"):
            self.master_pssw = self.master_pssw + self.salt
            self.cursor.execute("""SELECT id FROM passwords""")
            id = len(self.cursor.fetchall())
            while True:
                if id in self.cursor.execute("""SELECT id FROM passwords"""):
                    id += 1
                else: 
                    id += 1
                    break 

            infos = []
            stored_infos = [platform, mail, password, url]
            for i in stored_infos:
                try:
                    _iv, _ct = self.data_encrypt(i, self.master_pssw[0:32])
                except EmptyInput:
                    sys.exit(Fore.RED + 'The input cannot be empty. Please try again.' + Style.RESET_ALL)
                concatenate = _iv + "|" + _ct
                infos.append(concatenate)

            self.cursor.execute(f"""INSERT INTO passwords VALUES('{id}', '{infos[0]}', '{infos[1]}', '{infos[2]}', '{infos[3]}')""")
            self.datab.commit()

            print(
                Fore.GREEN + "\nThank you! Datas were added successfully.\n" + Style.RESET_ALL)

    def edit_password(self, option: str, new: str, id: int) -> None:
        """
        Update values in the database SQlite.

        Returns
            [str] the new password changed in the database
            - id [int]
        """
        if os.path.isfile('vault.db'):
            try:
                self.master_pssw = self.master_pssw + self.salt

            except KeyError:
                raise PasswordNotFound

            _iv, _ct = self.data_encrypt(new, self.master_pssw[0:32])
            ct_new_mail = _iv + "|" + _ct
            self.cursor.execute(
                f"""UPDATE passwords SET {option} = '{ct_new_mail}' WHERE id = '{id}'""")
            print(Fore.GREEN + f"The {option} has successfully changed to {new}." + Style.RESET_ALL)
            self.datab.commit()

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
            if os.path.isfile("vault.db"):
                try:
                    self.master_pssw = self.master_pssw + self.salt

                except KeyError:
                    raise PasswordNotFound

                infos = []
                for row in self.cursor.execute("""SELECT * FROM passwords"""):
                    infos.append(row[1])
                    infos.append(row[2])
                    infos.append(row[3])
                    infos.append(row[4])
                    decrypted = []
                    for i in infos:
                        decrypted.append(self.data_decrypt(str(i).split("|")[0], str(i).split("|")[1], self.master_pssw[0:32]))
                    
                    infos = []

                    print(f"ID: {row[0]}\nPlatform: {decrypted[0].decode()}\nEmail: {decrypted[1].decode()}\nPassword: {decrypted[2].decode()}\nURL: {decrypted[3].decode()}\n")

            else:
                raise DatabaseNotFound

    def delete_one(self, id: str) -> None:
        """
        Delete values in the Data Base SQlite.

        Arguments
            - id [int]
        """

        self.cursor.execute(
            f"DELETE from passwords WHERE id = '{id}'")
        self.datab.commit()
        print(Fore.GREEN +"\nThe password was deleted successfully.\n" + Style.RESET_ALL)
        self.cursor.execute("""SELECT * from passwords""")
        try:
            self.see_all()
        except DatabaseEmpty:
            print("\nThe database is empty. Try adding a password.")

        self.datab.commit()

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
            print(Fore.RED + "Deleting all data... (database)" + Style.RESET_ALL)
            print("Removing...")
            time.sleep(2)

            # Dropping the databale
            self.cursor.execute("""DROP TABLE passwords""")

            self.datab.commit()

            time.sleep(1)
            print(Fore.GREEN + "Done. All the passwords stored had been deleted with success." + Style.RESET_ALL)

    def delete_master(self):
        """Delete the master password and all the informations. It 
        is not possible decrypt the data without the master password.

        Returns 
            The database SQlitefile empty (.db)

        Raises 
            sqlite3.Error: error in the database  
            DatabaseNotFound: database was not found 

        """
        if os.path.isfile('vault.db'):
            print(Fore.RED + "Deleting all the passwords..." + Style.RESET_ALL)
            time.sleep(1)
            
            try:
                self.cursor.execute("""DROP TABLE passwords""")
                self.cursor.execute("""DROP TABLE masterpassword""")
                self.datab.commit()
                self.datab.close()

            except sqlite3.Error:
                raise

        else:
            raise DatabaseNotFound
