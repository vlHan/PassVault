# -*- coding: utf-8 -*-
from modules import *

import requests
import random
import getpass
import string
from time import sleep
from sys import exit


class Menu:
    """
    Menu class to grab informations from the user

    Arguments
        master_pw [str] -- master password
    """
    def __init__(self, master_pw: str) -> None:
        self.db = DataBase(master_pw)
        self.platform = None
        self.mail = None
        self.password = None
        self.url = None

    def __begin_informations(self) -> str:
        """
        Required informations to begin the program

        Returns
            Informations to store in the database  

        Raises 
            ConnectionError -- request does not work 
        """
        try: 
            self.platform = str(input("Enter the platform for which you want to store a password (ex. Google): ")).lower().strip().title()

            if self.platform.isnumeric() or self.platform.isspace():
                print(f"[red]{self.db.xmark_}Enter a valid answer[/red]")
                return self.__begin_informations()

            self.mail = str(input("Enter the email for this account: ")).lower().strip()
            self.url = str(input("Enter the URL of the website (ex. https://google.com): ")).lower().strip()

            if not self.url.startswith("http"):
                print(f"[red]{self.db.xmark_}Invalid URL. The URL must contain http:// or https:// in the beginning.[/red]")
                sleep(1)

                return self.__begin_informations()

            elif self.url.startswith("http"):
                try:
                    # Make a request in the URL gaved.
                    requests.get(self.url)

                except requests.ConnectionError:
                    # If the connection does not work, the URL is incorrect.
                    # Then the question will return
                    print(f"[red]{self.db.xmark_} Invalid URL.[/red]")
                    sleep(1)

                    return self.__begin_informations()

            want_gen = str(input(f"Do you want to generate a password for {self.platform}? (Y/n): ")).lower().strip()
            # Generate a password for a platform.
            if want_gen == "exit":
                exit("[cyan]Thanks for using.[/cyan]")

            elif want_gen == "y":
                try: 
                    return self.__generate_pass()
                except KeyboardInterrupt: 
                    exit(0)

            elif want_gen == "n":
                return getpass.getpass(prompt=f"Enter the password which you want to add for {self.platform} in the database: ").strip()

            else:
                print("[red]Enter a valid answer.[/red]")
                return self.__begin_informations()

        except KeyboardInterrupt:
            exit(0)

    def menu_interface(self) -> None:
        """
        Menu interface

        Raises 
            ConnectionError -- request does not work
            KeyboardInterrupt -- user interrupt the program
        """
        banner()
        print("[blue] 1) Add a password[/blue]")
        print("[blue] 2) Update informations[/blue]")
        print("[blue] 3) Look up passwords[/blue]")
        print("[red] 4) Delete a password (normal/master)[/red]")
        print("[red] 5) Delete all normal passwords[/red]")
        print("[red] 6) Exit the program[/red]")

        try:
            choice = str(input("\n └──Enter a choice: ")).strip()
        except KeyboardInterrupt: 
            exit(0)

        if choice in ["6", "exit"]:
            # Exit
            print("[cyan]Thanks for using.[/cyan]")
            exit(1)
        
        elif choice not in ["1", "2", "3", "4", "5", "6", "exit"]:
            print(f'[red]{self.db.xmark_} Invalid option.[/red]')
            sleep(1)
            return self.menu_interface()

        self.db.stored_passwords()
        print()
        if choice == "1":
            # add password
            self.password = self.__begin_informations()
            self.db.save_password(self.platform, self.mail, self.password, self.url)

        elif choice == "2":
            # update informations
            self.db.edit_password()

        elif choice == "3":
            # look up password
            self.db.look_up()

        elif choice == "4":
            # delete a password
            self.db.delete_one()

        elif choice == "5":
            # delete all passwords
            self.db.delete_all()
            
    def __generate_pass(self) -> None:
        """Returns generated password

        Returns
            [str] -- A random password

        """
        try:
            pwd_len = int(input("What length would you like your password to be? (At least 8) "))

            if pwd_len < 8:
                print(f"\n[red]{self.db.xmark_} The password is not long enough. Please try again.[/red]\n")
                return self.__generate_pass()
            else:
                print()
                for _ in range(1):
                    print(f'[yellow]Password for {self.platform}:[/yellow]', end=' ')
                    generated_password = ''.join(random.choice(string.ascii_uppercase + string.digits +
                                                string.ascii_lowercase + string.punctuation) for _ in range(pwd_len))
                    print(generated_password)
                enter_pw = str(
                    input("Do you want to use this password? (Y/n) ")).lower().strip()
                if enter_pw == 'y':
                    return generated_password

                elif enter_pw == 'n': 
                    print('\nReturning to the beginning...\n')
                    return self.__begin_informations()

                else:
                    print(f"[red]{self.db.xmark_} Enter a valid answer.[/red]")
                    return self.__generate_pass()
        
        except KeyboardInterrupt: 
            exit(0)
