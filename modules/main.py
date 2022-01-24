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

            self.master_pw = getpass.getpass(f'{Fore.CYAN}[PassVault]{Style.RESET_ALL} Enter your master password: ').strip()
            h = hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
            
            if h == master:
                while True:
                    Menu(self.master_pw).menu_interface()
                    sleep(1)

            else:
                print(f'{Fore.RED}The master password is not correct{Style.RESET_ALL}')
                self.main()
    
        except sqlite3.Error: 
            with sqlite3.connect('vault.db') as db: 
                cursor = db.cursor()
            print(f'{Fore.GREEN}To start, you have to create a master password. Be careful not to lose it as it is unrecoverable{Style.RESET_ALL}')
            try:
                master_pw = getpass.getpass(f'{Fore.CYAN}[PassVault]{Style.RESET_ALL} Create a master password to use the program: ')
                verify_master = getpass.getpass(f'{Fore.CYAN}[PassVault]{Style.RESET_ALL} Enter your master password again to verify it: ')
            except KeyboardInterrupt:
                exit(0)
                
            if master_pw == verify_master:
                if master_pw.isnumeric() or master_pw.isspace():
                    print(f'{Fore.RED}\nThe password is not correct. Please try again{Style.RESET_ALL}')
                    db.close()
                    return self.main()

                elif len(master_pw) < 8:
                    print(f'{Fore.RED}\nThe password must have at least 8 caracters.{Style.RESET_ALL}')
                    db.close()
                    return self.main()

                else:
                    cursor.execute("CREATE TABLE IF NOT EXISTS masterpassword (password TEXT NOT NULL, salt TEXT NOT NULL);")

                    salt = "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(32))
                    master = hmac.new(master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
                    
                    cursor.execute(f"INSERT INTO masterpassword VALUES('{master}', '{salt}')")
                    db.commit()
                    
                    exit(f"{Fore.GREEN}\nThank you! Restart the program and enter your master password to begin.{Style.RESET_ALL}")
            
            else:
                print(f'{Fore.RED }\nPassword do not match. Please try again.{Style.RESET_ALL}')
                db.close()
                return self.main()
