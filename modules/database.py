from modules import *

import random
import string


class Database:
    """
    Database is the class which contains database SQlite
    functions.
    
    If has an error which should not exist, please report 
    it at https://github.com/vlHan/PassVault/issues

    Arguments
        obj [Class] -- create instance of a class
        master_pw {str} -- master password
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
        self.encryption = Encryption()
    
    def query_command(self, sql: str, *args: object):
        """
        Query commands 

        Arguments
            sql {str} -- sqlite command
        """
        return self.obj_.cur.execute(sql, *args)
    
    def select_all(self, table: str) -> list:
        """
        Select all 

        Arguments 
            table {str} -- the table to be selected
            star {str} -- what select from the table
        """
        return self.query_command(f"SELECT * FROM {table}")
    
    def update_where(self, value: str, new: str, id_opt: str) -> None:
        """
        Update somewhere

        Arguments 
            value {str} -- the value to update
            new {str} -- new data to be informed
            id_opt {str} -- the id to be selected
        """
        self.query_command(f"UPDATE passwords SET {value} = '{new}' WHERE id = '{id_opt}'")
        self.obj_.conn.commit()
        
    def delete_where(self, id_opt: str) -> None:
        """
        Delete somewhere 

        Arguments 
            id_opt {str} -- the id to be deleted
        """
        self.query_command(f"DELETE FROM passwords WHERE id = '{id_opt}'")
        self.obj_.conn.commit()

    def drop_table(self, table: str) -> None: 
        """
        Drop tables

        Arguments 
            table {str} -- table to be deleted
        """
        self.query_command(f"DROP TABLE {table}")
        self.obj_.conn.commit()

    def verify_id(self, id_opt: str):
        """
        Verify if the ID is correct 

        Arguments
            id_opt {str} -- the id informed
        """
        id_list = [row[0] for row in self.select_all('passwords')]
        if id_opt not in str(id_list): 
            return print(f"[red]{self.obj_.xmark_} The ID is not correct[/]")
    
    def generate_password(self) -> str:
        """Returns generated password
        
        Returns
            {str} -- A random password
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
            platform {str} -- the platform of the password
            mail {str} -- email of the account
            password {str} -- password of the account to save in the database
            url {str} -- URL of the platform
        
        Returns 
            {tuple} -- Sensitives datas saved in the SQLite.
        
        The ID must be the length of the datas stored in the database plus one
        Then the user can change/delete informations.
        """
        id_db = len(self.query_command("SELECT id FROM passwords;").fetchall())

        while True:
            if id_db in self.query_command("SELECT id FROM passwords;"):
                # Verify if the ID exist in the database
                # if exist the code will add one more
                id_db += 1
            else: 
                id_db += 1
                break

        datas = []
        stored_infos = [platform, mail, password, url]
        for i in stored_infos:
            tag, nonce, contatenate = self.encryption.encrypt(i, self.master_pw)
            concatenate = f'{tag}|{nonce}|{contatenate}'
            datas.append(concatenate)

        # Insert each value in the table passwords
        self.query_command(f"INSERT INTO passwords VALUES('{id_db}', '{datas[0]}', '{datas[1]}', '{datas[2]}', '{datas[3]}')")
        self.obj_.conn.commit()

        print(f"[green]\n{self.obj_.checkmark_} Thank you! Datas were successfully added.[/green]")

    def edit_password(self, new: str, option: str, id_opt: str ) -> None:
        """
        Update values in the database SQlite.

        Arguments: 
            option {str} -- what need to be changed
            new {str} -- the new password
            id {str} -- the id of the data

        Returns
            {str} The new password changed in the database
        """
        self.verify_id(id_opt)

        tag, nonce, concatenate = self.encryption.encrypt(new, self.master_pw)
        concatenate_new_info = f'{tag}|{nonce}|{concatenate}'

        self.update_where(option, concatenate_new_info, id_opt)
        print(f"[green]{self.obj_.checkmark_} The {option} of the ID {id_opt} has successfully changed to {new}.[/green]")

    def look_up(self, id_opt: str) -> str:
        """
        See all passwords stored in the database.

        Arguments 
            id_opt {str} -- the ID chosed

        Returns
            {str} The passwords stored
        """
        self.verify_id(id_opt)
        infos = []
        for row in self.query_command(f"SELECT * FROM passwords WHERE id = '{id_opt}';"):
            infos.extend((row[1], row[2], row[3], row[4]))
            decrypted = [
                self.encryption.decrypt(
                    str(i).split("|")[0], 
                    str(i).split("|")[1],
                    str(i).split("|")[2],
                    self.master_pw
                )
                for i in infos
            ]

            infos.clear()
            return (
                f"\n[yellow][ID: {row[0]}] {decrypted[0]}[/yellow]\n"
                f"[green]Email: {decrypted[1]}\n"
                f"Password: {decrypted[2]}\n"
                f"URL: {decrypted[3]}[/green]\n"
            )

    def stored_passwords(self) -> None:
        """
        Stored passwords

        Returns 
            {str} -- List of passwords
        """
        if self.query_command("SELECT COUNT(*) from passwords;").fetchall()[0][0] == 0:
            # verify if the database is empty - cannot opperate in a empty database
            raise PermissionError

        print('[yellow]Current passwords stored:[/yellow]')
        infos = []
        for row in self.select_all('passwords'):
            infos.extend((row[1], row[2], row[3]))
            decrypted = [
                self.encryption.decrypt(
                    str(i).split("|")[0], 
                    str(i).split("|")[1],
                    str(i).split("|")[2],
                    self.master_pw
                )
                for i in infos
            ]

            infos.clear()
            print(f"[yellow][ID: {row[0]}] Platform: {decrypted[0]}[/yellow]")
        
    def delete_one_password(self, id_opt: str) -> None:
        """
        Delete one password

        Arguments 
            id_opt {str} -- the ID chosed
        """
        self.verify_id(id_opt)

        self.delete_where(id_opt)
        print(f"[green]\n{self.obj_.checkmark_} The password was successfully deleted.\n[/green]")

    def delete_all_passwords(self) -> None:
        """
        Delete all passwords stored in the database

        Arguments
            entered_master {str} -- master password to verify 
        """
        if self.query_command("SELECT COUNT(*) from passwords;").fetchall()[0][0] == 0: 
            # verify if the database is empty - cannot opperate in a empty database
            return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/]")

        self.drop_table('passwords')
        print(f"[green]{self.obj_.checkmark_} All normal passwords deleted successfully.[/green]")

    def delete_all_data(self):
        """
        Delete all data including the master password
        """
        self.drop_table("passwords")
        self.drop_table("masterpassword")
