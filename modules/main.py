# -*- coding: utf-8 -*-
from modules import *

import sqlite3
import hashlib 
import hmac
import getpass

from time import sleep
import random, string, os
from sys import exit

class Manager:
    def __init__(self) -> None:
        self.master_pw = None
        
    def main(self) -> None:
        """Main function to verify the user
        """
        if not os.path.isfile('vault.db'):
            sqlite3.connect('vault.db')
        try:
            cursor = sqlite3.connect('vault.db').cursor()
            cursor.execute("SELECT * FROM masterpassword")
            
            for inf in cursor.fetchall():
                master = inf[0]
                salt = inf[1] 
            print("[cyan][PassVault][/cyan] Enter the master password:", end = ' ')
            self.master_pw = getpass.getpass("").strip()
            h = hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
            
            if h == master:
                while True:
                    Menu(self.master_pw).menu_interface()
                    sleep(1)

            else:
                print('[red]The master password is not correct[/red]')
                self.main()
    
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
                exit(0)
                
            if self.master_pw == verify_master:
                if self.master_pw.isnumeric() or self.master_pw.isspace():
                    print('\n[red]The password is not correct. Please try again[/red]')
                    db.close()
                    return self.main()

                elif len(self.master_pw) < 8:
                    print('\n[red]The password must have at least 8 caracters.[/red]')
                    db.close()
                    return self.main()

                else:
                    cursor.execute("CREATE TABLE IF NOT EXISTS masterpassword (password TEXT NOT NULL, salt TEXT NOT NULL);")

                    salt = "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(32))
                    master = hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
                    
                    cursor.execute(f"INSERT INTO masterpassword VALUES('{master}', '{salt}')")
                    db.commit()
                    
                    print("\n[green]Thank you! Restart the program and enter your master password to begin.[/green]")
                    exit(1)
            
            else:
                print('\n[red]Password does not match. Please try again.[/red]')
                db.close()
                return self.main()
