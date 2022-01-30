from modules import *

import random
import string

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class DataConnect:
    """
    DataConnect is the class which contains database SQlite
    functions and encryption using AES and base 64.
    
    If has an error which should not exist, please report 
    it at https://github.com/vlHan/PassVault/issues

    Arguments
        obj [Class] -- create instance of a class
        master_pw [str] -- master password
    """

    def __init__(self, master_pssw: str, obj) -> None:
        # Connect with the SQlite and create the table.
        self.master_pw = master_pssw
        self.obj_ = obj
        self.query_command(
            """CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                platform TEXT NOT NULL,
                email TEXT NOT NULL, 
                password TEXT NOT NULL, 
                url TEXT NOT NULL
            );"""
        )
        self.specialchars = "_!@#$%&*()-"
    
    def query_command(self, sql: str, *args) -> None:
        """
        Query commands 

        Arguments
            sql [str] -- sqlite command
        """
        return self.obj_.cur.execute(sql, *args)
    
    def select_all(self, table: str) -> list:
        """
        Select all 

        Arguments 
            table [str] -- the table to be selected
            star [str] -- what select from the table
        """
        return self.query_command(f"SELECT * FROM {table}")
    
    def update_where(self, value: str, new: str, id_opt: str) -> None:
        """
        Update somewhere

        Arguments 
            value [str] -- the value to update
            new [str] -- new data to be informed
            id_opt [str] -- the id to be selected
        """
        cmd = self.query_command(f"UPDATE passwords SET {value} = '{new}' WHERE id = '{id_opt}'")
        self.obj_.conn.commit()
        
        return cmd
        
    def delete_where(self, id_opt: str) -> None:
        """
        Delete somewhere 

        Arguments 
            id_opt [str] -- the id to be deleted
        """
        cmd = self.query_command(f"DELETE FROM passwords WHERE id = '{id_opt}'")
        self.obj_.conn.commit()

        return cmd

    def drop_table(self, table: str) -> None: 
        """
        Drop tables

        Arguments 
            table [str] -- table to be deleted
        """
        self.query_command(f"DROP TABLE WHERE {table}")
        self.obj_.conn.commit()
    
    def delete_all_data(self):
        self.drop_table("passwords")
        self.drop_table("masterpassword")

    def verify_id(self, id_opt: str):
        """
        Verify if the ID is correct 

        Arguments
            id_opt [str] -- the id informed
        """
        id_list = [row[0] for row in self.select_all('passwords')]
        if id_opt not in str(id_list): 
            return print(f"[red]{self.obj_.xmark_} The ID is not correct[/]")

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
        pw_len = int(input("What length would you like your password to be? (At least 8) "))

        if pw_len < 8:
            print("\n[red] The password is not long enough. Please try again.[/]\n")
            return self.generate_password()
        else:
            # Generating a password
            password = [random.choice(random.choice([
                *self.specialchars,
                *string.ascii_lowercase,
                *string.ascii_uppercase,
                *string.digits
            ])) for _ in range(pw_len)]

            print(f'\n[yellow]Generated password:[/yellow] {"".join(password)}')
            return ''.join(password)

    def save_password(self, platform: str, mail: str, password: str, url: str) -> None:
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
        # The ID must be the length of the datas stored in the database plus one
        # then the user can change/delete informations.
        id = len(self.query_command("SELECT id FROM passwords;").fetchall())

        while True:
            if id in self.query_command("SELECT id FROM passwords;"):
                # Verify if the ID exist in the database
                # if exist the code will add one more
                id += 1
            else: 
                id += 1
                break 

        infos = []
        stored_infos = [platform, mail, password, url]
        for i in stored_infos:
            initial_value, contatenate = self.encryption(i, self.master_pw)
            concatenate = initial_value + "|" + contatenate
            infos.append(concatenate)
        # Insert each value in the table passwords
        self.query_command(f"INSERT INTO passwords VALUES('{id}', '{infos[0]}', '{infos[1]}', '{infos[2]}', '{infos[3]}')")
        self.obj_.conn.commit()

        print(f"[green]\n{self.obj_.checkmark_} Thank you! Datas were successfully added.[/green]")

    def edit_password(self, new: str, option: str, id_opt: str ) -> None:
        """
        Update values in the database SQlite.

        Arguments: 
            option [str] -- what need to be changed
            new [str] -- the new password
            id [str] -- the id of the data

        Returns
            [str] The new password changed in the database
        """
        self.verify_id(id_opt)
        
        initial_value, concatenate = self.encryption(new, self.master_pw)
        ct_new_info = initial_value + "|" + concatenate
        
        self.update_where(option, ct_new_info, id_opt)
        print(f"[green]{self.obj_.checkmark_} The {option} of the ID {id_opt} has successfully changed to {new}.[/green]")

    def look_up(self, id_opt: str) -> None:
        """
        See all passwords stored in the database.

        Arguments 
            id_opt [str] -- the ID chosed

        Returns
            [tuple] The passwords stored
        """
        self.verify_id(id_opt)
        infos = []
        for row in self.query_command(f"SELECT * FROM passwords WHERE id = '{id_opt}';"):
            infos.append(row[1])
            infos.append(row[2])
            infos.append(row[3])
            infos.append(row[4])

            decrypted = [
                self.decryption(
                    str(i).split("|")[0], 
                    str(i).split("|")[1],
                    self.master_pw
                )
                for i in infos
            ]
            
            infos.clear()
            return (
                f"\n[yellow][ID: {row[0]}] {decrypted[0].decode()}[/yellow]\n"
                f"[green]Email: {decrypted[1].decode()}\n"
                f"Password: {decrypted[2].decode()}\n"
                f"URL: {decrypted[3].decode()}[/green]\n"
            )

    def stored_passwords(self) -> None: 
        """
        Stored passwords

        Returns 
            [str] -- List of passwords
        """
        if self.query_command("SELECT COUNT(*) from passwords;").fetchall()[0][0] == 0:
            # verify if the database is empty - cannot opperate in a empty database
            raise PermissionError
        
        print('[yellow]Current passwords stored:[/yellow]')
        infos = []
        for row in self.select_all('passwords'):
            infos.append(row[1])
            infos.append(row[2])

            decrypted = [
                self.decryption(
                    str(i).split("|")[0], 
                    str(i).split("|")[1],
                    self.master_pw
                )
                for i in infos
            ]
            
            infos.clear()
            print(f"[yellow][ID: {row[0]}] Platform: {decrypted[0].decode()}[/yellow]")
        
    def delete_one_password(self, id_opt: str) -> None:
        """Delete one password

        Arguments 
            id_opt [str] -- the ID chosed
        """
        self.verify_id(id_opt)

        self.delete_where(id_opt)
        print(f"[green]\n{self.obj_.checkmark_} The password was successfully deleted.\n[/green]")

    def delete_all_passwords(self, entered_master: str) -> None:
        """
        Delete all passwords stored in the database 
        (Normal passwords not the master)

        Arguments
            entered_master [str] -- master password to verify 

        Returns
            DataBase empty (SQlite)
        """
        if self.query_command("SELECT COUNT(*) from passwords;").fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/]")

        if self.master_pw == entered_master:
            self.drop_table('passwords')
        else: 
            return print(f'[red]{self.obj_.xmark_} The master password is not correct.[/]')
            
