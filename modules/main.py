# -*- coding: utf-8 -*-
import hashlib
import hmac
import os
import getpass
import sys

from modules.menu import *


class Manager:
    def main(self, verify=False):
        """Main function to verify the user
        """
        if verify:
            Menu(self.master_pw).menu_interface()
            self.run()

        else:
            with sqlite3.connect('vault.db') as db: 
                cursor = db.cursor()

            if os.path.isfile('vault.db'):
                try: 
                    self.master_pw = getpass.getpass('Enter your master password: ')

                    cursor.execute("SELECT * FROM masterpassword")
                    for row in cursor.fetchall():
                        master = row[0]
                        salt = row[1] 

                    h = hmac.new(self.master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
                    if h == master:
                        Menu(self.master_pw).menu_interface()
                        self.run()
                    else:
                        print(Fore.RED + 'The master password is not correct.\033[0m')
                        self.main()
                    
                except sqlite3.Error:
                    print(Fore.GREEN + 'To start, you have to create a master password. Be careful not to lose it as it is unrecoverable.' + Style.RESET_ALL)
                    master_pw = getpass.getpass('Create a master password to use the program: ')
                    verify_master = getpass.getpass('Enter your master password again to verify it: ')
                    time.sleep(1)
                    
                    if master_pw == verify_master:
                        if master_pw.isnumeric() or master_pw.isspace():
                            print(Fore.RED + '\nThe password is not correct. Please try again.' + Style.RESET_ALL)
                            return self.main()

                        elif len(master_pw) < 8:
                            print(Fore.RED + '\nThe password must have at least 8 caracters.' + Style.RESET_ALL)
                            return self.main()

                        else:
                            with sqlite3.connect('vault.db') as db: 
                                cursor = db.cursor()
                                cursor.execute("CREATE TABLE masterpassword (password TEXT NOT NULL, salt TEXT NOT NULL);")

                            salt = "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(32))
                            master = hmac.new(master_pw.encode(), msg=str(salt).encode(), digestmod=hashlib.sha3_512).hexdigest()
                            
                            cursor.execute(f"INSERT INTO masterpassword VALUES('{master}', '{salt}')")
                            db.commit()
                            
                            sys.exit(
                                Fore.GREEN + "\nThank you! Restart the program and enter your master password to begin." + Style.RESET_ALL)

                    else:
                        print(Fore.RED + '\nPassword do not match. Please try again.' + Style.RESET_ALL)
                        return self.main()

    def run(self):
        """Declarate main() and runtime
        """
        time.sleep(1)
        options = str(
            input('\nDo you want to return to menu? (Y/n) ')).lower().strip()

        def runtime():
            time.sleep(2)
            print()
            print("*" * 41)
            print(Fore.CYAN + 'PassVault' + Style.RESET_ALL + ' finished.')
            print("Developed by vlHan. Thanks for using!")
            print("*" * 41)

        if options == 'y':
            self.main(verify=True)

        elif options == 'n':
            runtime()

        else:
            print(Fore.RED + 'Invalid option!' + Style.RESET_ALL)
            runtime()
