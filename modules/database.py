# -*- coding: utf-8 -*-
from modules import *

import sqlite3
import requests

from time import sleep
from sys import exit

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class DataBase:
    """
    DataBase is the class which contains database SQlite
    functions and encryption using AES and base 64.
    
    If has an error which should not exist, please report 
    it at https://github.com/vlHan/PassVault/issues
    """

    def __init__(self, master_pssw: str) -> None:
        self.datab = sqlite3.connect("vault.db")
        self.cursor = self.datab.cursor()
        self.checkmark_ = '\u2713'
        self.xmark_ = '\u2717'
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
        # Putting together the master password with the salt 
        # to use in the verificantion and in the encryption and decryption 
        self.master_pssw = master_pssw + self.salt


    def encryption(self, pssw: str, key: str) -> tuple:
        """
        Encrypt and save the data to a file using master password as the key

        Arguments
            pssw [str] -- password to be encrypted 
            key [str]  -- to encrypt and decrypt (masterpassword)

        Return 
            [str] initial value and the cyphertext in base64 (concatenate string)
        """
        if not pssw:
            print('[red]The input cannot be empty. Please try again.[/red]')
            return 

        pssw = pssw.encode('utf-8')
        key = key.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC)
        concatenate_bytes = cipher.encrypt(pad(pssw, AES.block_size))

        # pass the initial_value to base64
        iv = b64encode(cipher.iv).decode('utf-8')
        concatenate = b64encode(concatenate_bytes).decode('utf-8')  # cyphertext to base64

        return (iv, concatenate)

    def decryption(self, initial_value: str, ciphertext: str, key: str) -> str:
        """
        Encrypt data using master password as the key

        Arguments
            initial_value [str] -- the value to pass to base64
            ciphertext [str]  -- to encrypt and decrypt (masterpassword)
            key [str] -- the key to encrypt/decrypt passwords

        Returns 
            [str] The cypher text decrypted      
        """
        initial_value = b64decode(initial_value)
        concatenate = b64decode(ciphertext)
        key = key.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, initial_value)

        return unpad(cipher.decrypt(concatenate), AES.block_size) # try decrypt the cypher text

    def save_password(self, platform: str, mail: str, password: str, url: str) -> None:
        """
        Add values in the Database SQlite.

        Arguments 
            platform [str] -- the platform of the password
            mail [str] -- email of the account
            password [str] -- password of the account to save in the database
            url [str] -- URL of the platform
        """
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

        infos = []
        stored_infos = [platform, mail, password, url]

        for i in stored_infos:
            initial_value, contatenate = self.encryption(i, self.master_pssw[:32])
            concatenate = initial_value + "|" + contatenate
            infos.append(concatenate)
        # Insert each value in the table passwords
        self.cursor.execute(f"""INSERT INTO passwords VALUES('{id}', '{infos[0]}', '{infos[1]}', '{infos[2]}', '{infos[3]}')""")
        self.datab.commit()

        print(f"[green]\n{self.checkmark_} Thank you! Datas were successfully added.[/green]")

    def edit_password(self) -> None:
        """
        Update values in the database SQlite.

        Arguments: 
            option [str] -- what need to be changed
            new [str] -- the new password
            id [str] -- the id of the data

        Returns
            [str] The new password changed in the database
        """
        self.cursor.execute("SELECT COUNT(*) from passwords;")
        if self.cursor.fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

        else:
            try:
                option = str(input("What do you want to change? (platform/email/password/url) ")).lower().strip()
                new = str(input(f"\nEnter the new {option} which you want add in the database: ")).strip()
            except KeyboardInterrupt: 
                exit(0)

            if option == "url":
                if not new.startswith("http"):
                    print(f"[red]{self.xmark_}\n The URL must contain http:// or https:// in the beginning.[/red]\n")
                    sleep(1)
                    return self.edit_password()

                elif new.startswith("http"):
                    try:
                        # Make a request in the URL gaved.
                        requests.get(new)

                    except requests.ConnectionError:
                        # If the connection does not work, the URL is incorrect.
                        # Then the question will return
                        print(f"[red]\n{self.xmark_} Invalid URL. Please try again.\n[/red]")
                        sleep(1)
                        return self.edit_password()

            id = str(
                input(f"\nEnter the ID from the {option}: "))
                
            initial_value, concatenate = self.encryption(new, self.master_pssw[:32])
            ct_new_info = initial_value + "|" + concatenate
            
            self.cursor.execute(f"""UPDATE passwords SET {option} = '{ct_new_info}' WHERE id = '{id}'""")
            self.datab.commit()

            print(f"[red]{self.checkmark_} The {option} has successfully changed to {new}.[/red]")

    def look_up(self) -> None:
        """
        See all passwords stored in the database.

        Returns
            [tuple] The passwords stored
        """

        self.cursor.execute("SELECT COUNT(*) from passwords;")
        if self.cursor.fetchall()[0][0] == 0:
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

        else:
            try: 
                id = str(input('Enter ID for the password you want to retrieve: ')).strip()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt
            infos = []
            for row in self.cursor.execute(f"SELECT * FROM passwords WHERE id = '{id}';"):
                infos.append(row[1])
                infos.append(row[2])
                infos.append(row[3])
                infos.append(row[4])

                decrypted = [
                    self.decryption(
                        str(i).split("|")[0], 
                        str(i).split("|")[1],
                        self.master_pssw[:32]
                    )
                    for i in infos
                ]
                
                infos.clear()
                print(f"\n[yellow][ID: {row[0]}] {decrypted[0].decode()}[/yellow]\n[green]Email: {decrypted[1].decode()}\nPassword: {decrypted[2].decode()}\nURL: {decrypted[3].decode()}\n[/green]")

    def stored_passwords(self) -> None: 
        """Stored passwords
        """
        try:
            self.cursor.execute("SELECT COUNT(*) from passwords;")
        except sqlite3.OperationalError: 
            pass

        if self.cursor.fetchall()[0][0] != 0:
            print('[yellow]Current passwords stored:[/yellow]')

            infos = []
            for row in self.cursor.execute("SELECT * FROM passwords;"):
                infos.append(row[1])
                infos.append(row[2])

                decrypted = [
                    self.decryption(
                        str(i).split("|")[0], 
                        str(i).split("|")[1],
                        self.master_pssw[:32]
                    )
                    for i in infos
                ]
                
                infos.clear()
                print(f"[yellow][ID: {row[0]}] Platform: {decrypted[0].decode()}[/yellow]")

    def delete_one(self) -> None:
        """Delete one password
        """
        try:
            delete_pwd = str(input("Delete normal password or master password? (normal/master) ").lower().strip())

            if delete_pwd == "exit":
                exit("[cyan]Thanks for using.[/cyan]")

            elif delete_pwd == "":
                return self.delete_one()

            elif delete_pwd == "normal":
                self.cursor.execute("SELECT COUNT(*) from passwords;")
                if self.cursor.fetchall()[0][0] == 0: 
                    # verify if the database is empty - cannot opperate in a empty database
                    print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

                else:
                    id = str(input("Enter the ID of the password which you want delete: ")).strip()
                    self.cursor.execute(f"DELETE from passwords WHERE id = '{id}'")
                    self.datab.commit()
                    
                    print(f"[green]\n{self.checkmark_} The password was successfully deleted.\n[/green]")

            elif delete_pwd == "master":
                print('[red]NOTE: If you delete the master password you will lost all your sensitives data and will be logged out[/red]')
                confirm = str(input("Are you sure you want to delete the master password? (Y/n) ")).strip().lower()

                if confirm == "y":
                    print("[red]Deleting all the passwords...[/red]")
                    sleep(1)
                    self.cursor.execute("DROP TABLE passwords;")
                    self.cursor.execute("DROP TABLE masterpassword;")
                    self.datab.commit()
                    self.datab.close()
                    sleep(1)
                    print(f"[green]{self.checkmark_} Done! All passwods and the master password were successfully deleted.[/green]")
                    print('[red]Logging out...[/red]')
                    print('[cyan]Thanks for using.[/cyan]')
                    exit(1)
                
                elif confirm != "n": 
                    return self.delete_one()
        except KeyboardInterrupt: 
            exit(0)

    def delete_all(self) -> None:
        """
        Delete all passwords stored in the database 
        (Normal passwords not the master)

        Returns
            DataBase empty (SQlite)
        """
        self.cursor.execute("SELECT COUNT(*) from passwords;")
        if self.cursor.fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

        else:
            try:
                confirm = str(input("Are you sure you want to delete all normal passwords? (Y/n) ")).strip().lower()
                if confirm == "y":
                    print("[red]Deleting all data... (database)[/red]")
                    print("Removing...")
                    sleep(2)

                    # Dropping the datable
                    self.cursor.execute("DROP TABLE passwords;")
                    self.datab.commit()

                    sleep(1)
                    print(f"[green]{self.checkmark_} Done. All the passwords stored had been deleted with success.[/green]")

                elif confirm == "n":
                    pass

                elif confirm == "exit":
                    print("[cyan]Thanks for using.[/cyan]")
                    exit(1)

                elif confirm == "":
                    return self.delete_all()

                else:
                    print(f"[red]{self.xmark_} Invalid answer.[/red]")
                    return self.delete_all()
            
            except KeyboardInterrupt: 
                exit(0)
