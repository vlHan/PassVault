from modules import *

from time import sleep
import random, string
from sys import exit

import getpass
import sqlite3

from base64 import b64encode, b64decode
from backports.pbkdf2 import pbkdf2_hmac
import binascii


class Manager:
    def __init__(self) -> None:
        self.master_pw  = None
        self.conn = self.connect()
        self.cur = self.conn.cursor()
        self.xmark_ = '\u2717'
        self.checkmark_ = '\u2713'
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(f'./PassVault/{getpass.getuser()}.db')
            return self.conn
        except sqlite3.OperationalError: 
            self.conn = sqlite3.connect(f'./{getpass.getuser()}.db')
            return self.conn

    def exit_program(self) -> None:
        print("[red]Exiting the program...[/red]")
        exit(1)

    def main(self) -> None:
        """Main function to verify the user
        """
        try:
            self.cur.execute("SELECT * FROM masterpassword")
            for i in self.cur.fetchall():
                stored_master = i[0]
                salt = i[1] 

            print("[cyan][PassVault][/cyan] Enter the master password:", end=' ')
            self.master_pw = getpass.getpass("").strip()
            
            if b64encode(pbkdf2_hmac("sha3-512", self.master_pw.encode("utf-8"), str(salt).encode(), 500000)).decode() == stored_master:
                print(f'[green]{self.checkmark_} Logged with success![/green]')
                
                key = pbkdf2_hmac("sha3-256", self.master_pw.encode("utf-8"), str(salt).encode(), 500000, 16)
                self.master_pw = binascii.hexlify(key).decode()

                while True:
                    # create instance of menu class
                    menu = Menu(self.master_pw, Manager())
                    try:
                        sleep(1)
                        menu.begin_program()
                    except KeyboardInterrupt:
                        self.exit_program()

            else:
                print(f'[red]{self.xmark_} The master password is not correct[/red]')
                return self.main()
    
        except sqlite3.Error: 
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
                    print(f'\n[red]{self.checkmark_} The password is not correct. Please try again[/red]')
                    return self.main()

                elif len(self.master_pw) < 8:
                    print(f'\n[red]{self.xmark_} The password must have at least 8 caracters.[/red]')
                    return self.main()

                else:
                    self.cur.execute("CREATE TABLE IF NOT EXISTS masterpassword (password TEXT NOT NULL, salt TEXT NOT NULL);")
                    salt = "".join(random.choice(
                            string.ascii_uppercase + 
                            string.digits + 
                            string.ascii_lowercase
                        ) for _ in range(32)
                    )
                    master = b64encode(pbkdf2_hmac("sha3-512", self.master_pw.encode("utf-8"), str(salt).encode(), 500000)).decode()
                    self.cur.execute(f"INSERT INTO masterpassword VALUES('{master}', '{salt}')")
                    self.conn.commit()
                    
                    print(f"\n[green]{self.checkmark_} Thank you! Restart the program and enter your master password to begin.[/green]")
                    exit(1)
            
            else:
                print(f'\n[red]{self.checkmark_} Password do not match. Please try again.[/red]')
                return self.main()
