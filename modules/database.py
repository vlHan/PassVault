# -*- coding: utf-8 -*-
from modules import *

import sqlite3
import random
import string

from time import sleep

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

    def __init__(self) -> None:
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
        # Putting together the master password with the salt 
        # to use in the verificantion and in the encryption and decryption 
        self.specialchars = "_!@#$%&*()-"
        self.xmark_ = '\u2717'
        self.checkmark_ = '\u2713'

    def encryption(self, pssw: str, key: str) -> tuple:
        """
        Encrypt and save the data to a file using master password as the key

        Arguments
            pssw [str] -- password to be encrypted 
            key [str]  -- to encrypt and decrypt (masterpassword)

        Return 
            [str] initial value and the cyphertext in base64 (concatenate string)
        """

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
    
    def generate_password(self) -> None:
        """Returns generated password

        Returns
            [str] -- A random password
        """
        pwd_len = int(input("What length would you like your password to be? (At least 8) "))

        if pwd_len < 8:
            print("\n[red] The password is not long enough. Please try again.[/red]\n")
            return self.generate_password()
        else:
            # Generating a password
            password = [random.choice(random.choice([
                string.ascii_lowercase,
                string.ascii_uppercase,
                string.digits,
                self.specialchars
            ])) for _ in range(pwd_len)]

            print('\n[yellow]Generated password:[/yellow]', ''.join(password))
            return ''.join(password)

    def save_password(self, platform: str, mail: str, password: str, url: str, master_pssw: str) -> None:
        """
        Add values in the Database SQlite.

        Arguments 
            platform [str] -- the platform of the password
            mail [str] -- email of the account
            password [str] -- password of the account to save in the database
            url [str] -- URL of the platform
        
        Returns 
            [tuple] -- Sensitives datas saved in the SQLite.
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
        master_pss = master_pssw + self.salt
        for i in stored_infos:
            initial_value, contatenate = self.encryption(i, master_pss[:32])
            concatenate = initial_value + "|" + contatenate
            infos.append(concatenate)
        # Insert each value in the table passwords
        self.cursor.execute(f"""INSERT INTO passwords VALUES('{id}', '{infos[0]}', '{infos[1]}', '{infos[2]}', '{infos[3]}')""")
        self.datab.commit()

        print(f"[green]\n{self.checkmark_} Thank you! Datas were successfully added.[/green]")

    def edit_password(self, master_pssw: str, new: str, option: str, id_opt: str ) -> None:
        """
        Update values in the database SQlite.

        Arguments: 
            master_pssw [str] -- master password
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
                self.cursor.execute(f"SELECT from passwords WHERE id = '{id_opt}'")
            except sqlite3.Error: 
                return print(f"[red]{self.xmark_} The ID is not correct[/red]") 
            else: 
                master_pss = master_pssw + self.salt
                initial_value, concatenate = self.encryption(new, master_pss[:32])
                ct_new_info = initial_value + "|" + concatenate
                
                self.cursor.execute(f"""UPDATE passwords SET {option} = '{ct_new_info}' WHERE id = '{id_opt}'""")
                self.datab.commit()

                print(f"[red]{self.checkmark_} The {option} has successfully changed to {new}.[/red]")

    def look_up(self, master_pssw: str, id_opt: str) -> None:
        """
        See all passwords stored in the database.

        Arguments 
            master_pssw [str] -- the master password
            id_opt [str] -- the ID chosed

        Returns
            [tuple] The passwords stored
        """

        self.cursor.execute("SELECT COUNT(*) from passwords;")
        if self.cursor.fetchall()[0][0] == 0:
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

        else:
            try: 
                self.cursor.execute(f"SELECT from passwords WHERE id = '{id_opt}'")
            except sqlite3.Error: 
                return print(f"[red]{self.xmark_} The ID is not correct[/red]")
            else: 
                master_pss = master_pssw + self.salt
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
                            master_pss[:32]
                        )
                        for i in infos
                    ]
                    
                    infos.clear()
                    print(f"\n[yellow][ID: {row[0]}] {decrypted[0].decode()}[/yellow]\n[green]Email: {decrypted[1].decode()}\nPassword: {decrypted[2].decode()}\nURL: {decrypted[3].decode()}\n[/green]")

    def stored_passwords(self, master_pssw: str) -> None: 
        """Stored passwords
        """
        try:
            self.cursor.execute("SELECT COUNT(*) from passwords;")
        except sqlite3.OperationalError: 
            pass

        if self.cursor.fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            raise PermissionError

        print('[yellow]Current passwords stored:[/yellow]')
        master_pss = master_pssw + self.salt
        infos = []
        for row in self.cursor.execute("SELECT * FROM passwords;"):
            infos.append(row[1])
            infos.append(row[2])

            decrypted = [
                self.decryption(
                    str(i).split("|")[0], 
                    str(i).split("|")[1],
                    master_pss[:32]
                )
                for i in infos
            ]
            
            infos.clear()
            print(f"[yellow][ID: {row[0]}] Platform: {decrypted[0].decode()}[/yellow]\n")
            
    def delete_normal(self, id_opt: str) -> None:
        """Delete one password

        Arguments 
            id_opt [str] -- the ID chosed
        """
        self.cursor.execute("SELECT COUNT(*) from passwords;")
        if self.cursor.fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

        else:
            try:
                self.cursor.execute(f"SELECT from passwords WHRE id = '{id_opt}'")
            except sqlite3.DatabaseError: 
                print(f'[red]{self.xmark_} The ID is not correct.[/red]')
            else:
                self.cursor.execute(f"DELETE from passwords WHERE id = '{id_opt}'") 
                self.datab.commit()
                print(f"[green]\n{self.db.checkmark_} The password was successfully deleted.\n[/green]")

    def delete_master(self):
        """
        Delete master password all the data
        """
        self.cursor.execute("SELECT COUNT(*) from passwords;")
        if self.cursor.fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.xmark_} The database is empty. Try adding a password.[/red]")

        else:
            self.cursor.execute("DROP TABLE passwords;")
            self.cursor.execute("DROP TABLE masterpassword;")
            self.datab.commit()

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
            print("[red]Deleting all data... (database)[/red]")
            print("Removing...")
            sleep(2)

            # Dropping the datable
            self.cursor.execute("DROP TABLE passwords;")
            self.datab.commit()

            sleep(1)
            print(f"[green]{self.checkmark_} Done. All the passwords stored had been deleted with success.[/green]")
            exit('[red]Exiting...[/red]')