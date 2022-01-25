# -*- coding: utf-8 -*-
from modules import *

import sqlite3
import hashlib 
import hmac
import getpass

from time import sleep
import random, string
from sys import exit

class Manager:
    """
    Manager class 
    
    Arguments
        obj [Function] -- create instance of a class
    """
    def __init__(self, obj) -> None:
        self.master_pw  = None
        self.obj_ = obj
    
    def exit_program(self) -> None:
        print("[red]Exiting the program...[/red]")
        exit(1)

    def main(self) -> None:
        """Main function to verify the user
        """
        try:
            cursor = sqlite3.connect('vault.db').cursor()
            cursor.execute("SELECT * FROM masterpassword")
            
            for row in cursor.fetchall():
                stored_master = row[0]
                salt = row[1] 

            print("[cyan][PassVault][/cyan] Enter the master password:", end=' ')
            self.master_pw = getpass.getpass("").strip()
            
            if hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest() == stored_master:
                print(f'[green]{self.obj_.checkmark_} Logged with success![/green]')
                while True:
                    # create instance of menu class
                    menu = Menu(self.master_pw)

                    try:
                        menu.begin_program()
                        sleep(1)
                    except KeyboardInterrupt: 
                        self.exit_program()

            else:
                print(f'[red]{self.obj_.xmark_} The master password is not correct[/red]')
                return self.main()
    
        except sqlite3.Error: 
            with sqlite3.connect('vault.db') as db: 
                cursor = db.cursor()
            print('[green]To start, you have to create a master password. Be careful not to lose it as it is unrecoverable[/green]')
            
            try:
                print('[cyan][PassVault][/cyan] Create a master password to use the program:', end=' ')
                self.master_pw = getpass.getpass("")
                print('[cyan][PassVault][/cyan] Enter your master password again to verify it:', end=' ')
                verify_master = getpass.getpass("")
            except KeyboardInterrupt:
                self.exit_program()
                
            if self.master_pw == verify_master:
                if self.master_pw.isnumeric() or self.master_pw.isspace():
                    print(f'\n[red]{self.obj_.checkmark_} The password is not correct. Please try again[/red]')
                    return self.main()

                elif len(self.master_pw) < 8:
                    print(f'\n[red]{self.obj_.xmark_} The password must have at least 8 caracters.[/red]')
                    return self.main()

                else:
                    cursor.execute("CREATE TABLE IF NOT EXISTS masterpassword (password TEXT NOT NULL, salt TEXT NOT NULL);")
                    salt = "".join(random.choice(string.ascii_uppercase + 
                                                string.digits + 
                                                string.ascii_lowercase) for _ in range(32))
                    master = hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
                    cursor.execute(f"INSERT INTO masterpassword VALUES('{master}', '{salt}')")
                    db.commit()
                    
                    print(f"\n[green]{self.obj_.checkmark_} Thank you! Restart the program and enter your master password to begin.[/green]")
                    exit(1)
            
            else:
                print(f'\n[red]{self.obj_.checkmark_} Password do not match. Please try again.[/red]')
                return self.main()
