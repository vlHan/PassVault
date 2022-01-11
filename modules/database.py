# -*- coding: utf-8 -*-
from modules import *

import sqlite3
import time
import os
from colorama import Fore, Style 

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class DataBase:
    """
    DataBase is the class which contains database SQlite
    functions and encryption using AES and base 64.
    
    If has an error which should not exist, please report it at 
    https://github.com/vlHan/PassVault/issues
    """

    def __init__(self, master_pssw: str) -> None:
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
        self.cursor.execute("SELECT * FROM masterpassword;")
        for row in self.cursor.fetchall():
            # Select the salt of the master password
            self.salt = row[1] 
        # Here I am putting together the master password with the salt 
        # to use in the verificantion and in the encryption and decryption 
        self.master_pssw = master_pssw + self.salt


    def encryption(self, pssw: str, key: str) -> None:
        """
        Encrypt and save the data to a file using master password as the key

        Arguments
            - pssw [str] = password to be encrypted 
            - key [str]  = to encrypt and decrypt (masterpassword)

        Variables 
            - cipher = cipher is the initialization vector to use for encryption or decryption.
            - concatenate_bytes = returns the cypher text
            - iv = initial value 
            - concatenate
        """
        if not pssw:
            print(Fore.RED + 'The input cannot be empty. Please try again.' + Style.RESET_ALL)
            return 

        pssw = pssw.encode('utf-8')
        key = key.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC)
        concatenate_bytes = cipher.encrypt(pad(pssw, AES.block_size))

        # pass the initial_value to base64
        iv = b64encode(cipher.iv).decode('utf-8')
        concatenate = b64encode(concatenate_bytes).decode('utf-8')  # cyphertext to base64

        return (iv, concatenate)

    def decryption(self, initial_value: str, ciphertext: str, key: str) -> None:
        """
        Encrypt data using master password as the key

        Returns 
            The initial_value text        
        """
        initial_value = b64decode(initial_value)
        concatenate = b64decode(ciphertext)
        key = key.encode('utf-8')

        cipher = AES.new(key, AES.MODE_CBC, initial_value)
        # try decrypt the cypher text
        pt = unpad(cipher.decrypt(concatenate), AES.block_size)
        
        return pt

    def save_password(self, platform: str, mail: str, password: str, url: str) -> None:
        """
        Add values in the Database SQlite.
        """
        if os.path.isfile("vault.db"):
            self.cursor.execute("SELECT id FROM passwords;")
            # The ID must be the length of the datas stored in the database plus one
            # then the user can change/delete informations.
            id = len(self.cursor.fetchall())

            while True:
                if id in self.cursor.execute("SELECT id FROM passwords;"):
                    # Verify if the ID exist in the database
                    # if exist the code will add one more
                    id += 1
                else: 
                    id += 1
                    break 

            infos = list()
            stored_infos = [platform, mail, password, url]
            for i in stored_infos:
                initial_value, contatenate = self.encryption(i, self.master_pssw[0:32])
                concatenate = initial_value + "|" + contatenate
                infos.append(concatenate)
            # Insert each value in the table passwords
            self.cursor.execute(f"""INSERT INTO passwords VALUES('{id}', '{infos[0]}', '{infos[1]}', '{infos[2]}', '{infos[3]}')""")
            self.datab.commit()

            print(
                Fore.GREEN + "\nThank you! Datas were added successfully.\n" + Style.RESET_ALL)

    def edit_password(self, option: str, new: str, id: int) -> None:
        """
        Update values in the database SQlite.

        Arguments: 
            option [str] = what need to be changed
            new [str] = the new password
            id [str] = the id of the data

        Returns
            [str] the new password changed in the database
        """
        if os.path.isfile('vault.db'):
            initial_value, concatenate = self.encryption(new, self.master_pssw[0:32])
            ct_new_info = initial_value + "|" + concatenate
            
            self.cursor.execute(f"""UPDATE passwords SET {option} = '{ct_new_info}' WHERE id = '{id}'""")
            print(Fore.GREEN + f"The {option} has successfully changed to {new}." + Style.RESET_ALL)
            self.datab.commit()

        else:
            print(Fore.RED + 'Database was not found.' + Style.RESET_ALL)

    def see_all(self) -> None:
        """
        See all passwords stored in the database.

        Returns
            - [tuple] The passwords stored
        """

        self.cursor.execute("SELECT COUNT(*) from passwords;")
        result = self.cursor.fetchall()

        if result[0][0] == 0:
            # verify if the database is empty - cannot opperate in a empty database
            print(Fore.RED + "\nThe database is empty. Try adding a password." + Style.RESET_ALL)

        else:
            print()
            if os.path.isfile("vault.db"):
                infos = list()
                for row in self.cursor.execute("SELECT * FROM passwords;"):
                    infos.append(row[1])
                    infos.append(row[2])
                    infos.append(row[3])
                    infos.append(row[4])

                    decrypted = list()
                    for i in infos:
                        decrypted.append(
                            self.decryption(
                                str(i).split("|")[0], 
                                str(i).split("|")[1],
                                self.master_pssw[0:32]
                        ))
                    
                    infos.clear()

                    print(f"ID: {row[0]}\nPlatform: {decrypted[0].decode()}\nEmail: {decrypted[1].decode()}\nPassword: {decrypted[2].decode()}\nURL: {decrypted[3].decode()}\n")

            else:
                print(Fore.RED + 'Database was not found.' + Style.RESET_ALL)

    def delete_one(self, id: str) -> None:
        self.cursor.execute(f"DELETE from passwords WHERE id = '{id}'")
        self.datab.commit()

    def delete_pwds(self) -> None:
        """
        Delete all passwords stored in the database 
        (Normal passwords not the master)

        Returns
            DataBase empty (SQlite)
        """
        self.cursor.execute("SELECT COUNT(*) from passwords;")
        result = self.cursor.fetchall()

        # verify if the database is empty - cannot opperate in a empty database
        if result[0][0] == 0:
            print(Fore.RED + "\nThe database is empty. Try adding a password." + Style.RESET_ALL)

        else:
            print(Fore.RED + "Deleting all data... (database)" + Style.RESET_ALL)
            print("Removing...")
            time.sleep(2)

            # Dropping the databale
            self.cursor.execute("DROP TABLE passwords;")
            self.datab.commit()

            time.sleep(1)
            print(Fore.GREEN + "Done. All the passwords stored had been deleted with success." + Style.RESET_ALL)

    def delete_master(self) -> None:
        """Delete the master password and all the informations. It 
        is not possible decrypt the data without the master password.

        Returns 
            The database SQlitefile empty (.db)
        """
        if os.path.isfile('vault.db'):
            print(Fore.RED + "Deleting all the passwords..." + Style.RESET_ALL)
            time.sleep(1)
            
            try:
                self.cursor.execute("DROP TABLE passwords;")
                self.cursor.execute("DROP TABLE masterpassword;")
                self.datab.commit()
                self.datab.close()

            except sqlite3.Error:
                raise

        else:
            print(Fore.RED + 'Database was not found.' + Style.RESET_ALL)
