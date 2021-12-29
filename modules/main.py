# -*- coding: utf-8 -*-
import timeit
import hashlib
import hmac
import os
import json
import getpass
import sys

from modules.menu import *

__author__ = "vlHan"
__version__ = "V1.0"


class Manager:
    def main(self, verify=False):
        """Main function to verify the user
        """
        if verify:
            Menu(self.master_pw).menu_interface()
            self.run()

        else:
            if os.path.isfile('db/info.json'):
                with open("db/info.json", 'r') as f:
                    jfile = json.load(f)

                self.master_pw = getpass.getpass(
                    'Enter your master password: ')

                h = hmac.new(self.master_pw.encode(), msg=str(
                    jfile["Informations"]["salt"]).encode(), digestmod=hashlib.sha3_512).hexdigest()

                if h == jfile["Informations"]["master_password"]:
                    Menu(self.master_pw).menu_interface()
                    self.run()

                else:
                    print(Fore.RED + 'The master password is not correct.\033[0m')
                    self.main()

            else:
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
                        try:
                            os.mkdir('db/')
                        except Exception:
                            pass

                        jfile = {"Informations": {}}
                        jfile["Informations"]["salt"] = "".join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(32))
                        jfile["Informations"]["master_password"] = hmac.new(master_pw.encode(), msg=str(jfile["Informations"]["salt"]).encode(), digestmod=hashlib.sha3_512).hexdigest()
                        with open('db/info.json', 'w', encoding='utf-8') as jsondata:
                            json.dump(jfile, jsondata, sort_keys=True, indent=4)

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
            start = timeit.default_timer()
            print("*" * 41)
            print(Fore.CYAN + 'PassVault' + Style.RESET_ALL + ' finished.')

            end = timeit.default_timer()
            print("\n[+] RUNTIME: %f seconds\n" % (end - start))
            print("[+] Developed by vlHan. Thanks for using!")
            print("*" * 41)

        if options == 'y':
            self.main(verify=True)

        elif options == 'n':
            runtime()

        else:
            print(Fore.RED + 'Invalid option!' + Style.RESET_ALL)
            runtime()
