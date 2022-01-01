# -*- coding: utf-8 -*-
import requests
import random
import getpass
import string
import time
import sys
import sqlite3

from modules.banner import *
from modules.database import DataBase
from modules.exceptions import *


class Menu:
    def __init__(self, master_pw: str) -> None:
        """
        Menu interface

        Arguments
            - master_pw [str] = master password

        Variables
            - db [class] = database class
            - platform [str]
            - mail [str]
            - password [str]
            - url [str]
        """
        self._db = DataBase(master_pw)
        self._platform = ""
        self._mail = ""
        self._password = ""
        self._url = ""

    def __begin_informations(self) -> str:
        """
        Required informations to begin the program
            Inform what you will store.

        Returns
            Informations to store in the database  

        Raises 
            ConnectionError: request does not work 
        """
        self._platform = str(input("Enter the platform for which you want to store a password (ex. Google): ")).lower().strip().title()

        if self._platform == "exit":
            banner()
            sys.exit(Fore.GREEN + "Thanks for using." + Style.RESET_ALL)

        if self._platform.isnumeric() or self._platform.isspace():
            print(Fore.RED + "Enter a valid answer" + Style.RESET_ALL)
            return self.__begin_informations()

        self._mail = str(input(f"Enter the email for this account: ")).lower().strip()
        self._url = str(input(f"Enter the URL of the website (ex. https://google.com): ")).lower().strip()

        if not self._url.startswith("http"):
            print(Fore.RED + "Invalid URL. The URL must contain http:// or https:// in the beginning." + Style.RESET_ALL)
            time.sleep(1)

            return self.__begin_informations()

        elif self._url.startswith("http"):
            try:
                # Make a request in the URL gaved.
                requests.get(self._url)

            except sqlite3.ConnectionError:
                # If the connection does not work, the URL is incorrect.
                # Then the question will return
                print(Fore.RED + "Invalid URL." + Style.RESET_ALL)
                time.sleep(1)

                return self.__begin_informations()

        want_gen = str(input(f"Do you want to generate a password for {self._platform}? (Y/n): ")).lower().strip()
        # Generate a password for a platform.
        if want_gen == "exit":
            banner()
            sys.exit(Fore.GREEN + "Thanks for using." + Style.RESET_ALL)

        elif want_gen == "y":
            try:
                return self.__generate_pass()
            except CharNotLongEnough:
                print(Fore.RED + "\nThe password is not long enough. Please try again.\n" + Style.RESET_ALL)
                return self.__generate_pass()

        elif want_gen == "n":
            self._password = getpass.getpass(prompt=f"Enter the password which you want to add for {self._platform} in the database (ex. password123): ").strip()

        else:
            print(Fore.RED + "Enter a valid answer." + Style.RESET_ALL)
            return self.__begin_informations()

    def menu_interface(self) -> None:
        """
        Menu interface
            - ask for a choice

        Raises 
            DatabaseEmpty: the database is empty
            ConnectionError: request does not work 
        """
        banner()
        print(Fore.BLUE + " 1) Add a password" + Style.RESET_ALL)
        print(Fore.BLUE + " 2) Update informations" + Style.RESET_ALL)
        print(Fore.BLUE + " 3) Look up the password" + Style.RESET_ALL)
        print(Fore.RED + " 4) Delete a password (normal/master)" +
              Style.RESET_ALL)
        print(Fore.RED + " 5) Delete all normal passwords" + Style.RESET_ALL)
        print(Fore.RED + " 6) Exit the program" + Style.RESET_ALL)

        ask = str(input("\n └──Enter a choice: ")).strip()
        if ask == "1":
            # add password
            self.__begin_informations()
            self._db.save_password(self._platform, self._mail,
                                  self._password, self._url)

        elif ask == "2":
            # update informations
            try:
                self._db.see_all()
            except DatabaseEmpty:
                print(Fore.RED + "\nThe database is empty. Try adding a password." + Style.RESET_ALL)

            option = str(input("What do you want to change? (platform/email/password/url) ")).lower().strip()

            if option == "platform" or "email" or "password" or "url":
                new = str(input(f"\nEnter the new {option} which you want add in the database: ")).strip()

                if option == "url":
                    if not new.startswith("http"):
                        print(
                            Fore.RED + "\nInvalid URL. The URL must contain http:// or https:// in the beginning.\n" + Style.RESET_ALL)
                        time.sleep(1)
                        return self.menu_interface()

                    elif new.startswith("http"):
                        try:
                            # Make a request in the URL gaved.
                            requests.get(new)

                        except sqlite3.ConnectionError:
                            # If the connection does not work, the URL is incorrect.
                            # Then the question will return
                            print(Fore.RED + "\nInvalid URL. Please try again.\n" +
                                  Style.RESET_ALL)
                            time.sleep(1)
                            return self.menu_interface()

            else:
                print(Fore.RED + "Enter a valid answer" + Style.RESET_ALL)
                return self.menu_interface()

            id = str(
                input(f"\nEnter the id of the {option}: "))
            self._db.edit_password(option, new, id)

        elif ask == "3":
            # look up password
            try:
                self._db.see_all()
            except DatabaseEmpty:
                print(Fore.RED + "\nThe database is empty. Try adding a password." + Style.RESET_ALL)

        elif ask == "4":
            # delete a password
            self.delete_one()

        elif ask == "5":
            # delete all passwords
            self.delete_all()

        elif ask == "6":
            # Exit
            banner()
            sys.exit(Fore.GREEN + "Thanks for using." + Style.RESET_ALL)

        elif ask == "exit":
            # If it is exit, the program will finish.
            sys.exit(Fore.RED + "Thanks for using." + Style.RESET_ALL)

        else:
            print(Fore.RED + "Invalid option." + Style.RESET_ALL)
            return self.menu_interface()

    def __generate_pass(self):
        """Returns generated password

        Returns
            - [str] A randomly generated password

        Raises
            CharNotLongEnough: the password is not long enough
        """
        pwd_len = int(input("What length would you like your password to be? "))
        pwd_count = int(input("How many passwords would you like? "))

        if pwd_len < 3:
            raise CharNotLongEnough
        else:
            print()
            for _ in range(pwd_count):
                print(''.join(random.choice(string.ascii_uppercase + string.digits +
                                            string.ascii_lowercase + string.punctuation) for _ in range(pwd_len)))
            enter_pw = str(
                input("Enter the password generated which you want to use: ")).strip()
            if not enter_pw.isspace() or not enter_pw == "":
                self._password = enter_pw

            else:
                print(Fore.RED + "Enter a valid answer." + Style.RESET_ALL)
                return self.__generate_pass()

    def delete_one(self) -> None:
        """
        Delete a line of the table, a normal password or master password.

        Raises 
            DatabaseNotFound: the database was not found
        """
        delete_pwd = str(input("Do you want to delete a normal password or the master password? (normal/master) ").lower().strip())

        if delete_pwd == "exit":
            sys.exit(Fore.RED + "Thanks for using." + Style.RESET_ALL)
        elif delete_pwd == "":
            return self.delete_one()
        else:
            if delete_pwd == "normal":
                """Delete a normal password stored in the database SQlite.
                """
                print(Fore.RED + 'NOTE: If you delete a normal password the information which is together will also be deleted.' + Style.RESET_ALL)
                self._db.see_all()
                id = str(input("Enter the id of the password which you want to delete: ")).strip()

                self._db.delete_one(id)

            elif delete_pwd == "master":
                """Delete the master password and all the informations. It 
                is not possible decrypt the data without the master password.
                """
                print(
                    Fore.RED + 'NOTE: If you delete the master password you will lost all your sensitives data and will be logged out' + Style.RESET_ALL)
                confirm = str(input("Are you sure you want to delete the master password? (Y/n) ")).strip().lower()
                if confirm == "y":
                    try:
                        self._db.delete_master()
                        time.sleep(1)

                        print(Fore.GREEN + "Done. All the passwods including the master password had been deleted with success." + Style.RESET_ALL)
                        time.sleep(1)

                        print(Fore.RED + 'Now you will be logged out.' + Style.RESET_ALL)
                        time.sleep(2)

                        banner()
                        sys.exit(Fore.GREEN + 'Thanks for using.' + Style.RESET_ALL)

                    except DatabaseNotFound:
                        print(Fore.RED + 'Database was not found. Try to reload the program' + Style.RESET_ALL)
                        return self.delete_one()

                elif confirm == "n":
                    banner()
                    sys.exit(Fore.GREEN + "Thanks for using." + Style.RESET_ALL)

                else:
                    print(Fore.RED + "Enter a valid answer." + Style.RESET_ALL)
                    self.delete_all()

            else:
                print(Fore.RED + "Enter a valid answer." + Style.RESET_ALL)
                self.delete_one()

    def delete_all(self):
        """
        Delete all passwords stored.

        Raises 
            DatabaseNotFound: the database was not found
        """
        confirm = (str(input(
            "Are you sure you want to delete all normal passwords? (Y/n) ")).strip().lower())

        if confirm == "y":
            try:
                self._db.delete_pwds()
            except DatabaseEmpty:
                print("\nThe database is empty. There are no passwords stored to delete.\n")
        elif confirm == "n":
            pass
        elif confirm == "exit":
            sys.exit(Fore.GREEN + "Thanks for using." + Style.RESET_ALL)
        elif confirm == "":
            return self.delete_all()
        else:
            print(Fore.RED + "Invalid answer ")
            return self.delete_all()
