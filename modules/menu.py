# -*- coding: utf-8 -*-
from modules import *

import requests
import getpass

from time import sleep
from sys import exit


class Menu:
    """
    Menu class to grab informations from the user

    Arguments
        master_pw [str] -- master password
    """
    def __init__(self, master_pw: str, obj) -> None:
        self.obj_ = obj
        self.db = DataBase(obj, master_pw)

    def begin_program(self) -> str:
        """
        Beginning of the program

        Raises: 
            KeyboardInterrupt -- user interrupts

        Returns
            Informations to store in the database  
        """
        choice = self.menu_interface()
        if choice in ["6", "exit"]:
            # Exit
            print("[cyan]Thanks for using.[/cyan]")
            exit(1)

        elif choice == "1":
            # add password
            try:
                platform, mail, password, url = self.inform_data()
                self.db.save_password(platform, mail, password, url)
            except KeyboardInterrupt: 
                raise KeyboardInterrupt

        elif choice == "2":
            # edit informations
            try:
                self.edit_password()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt

        elif choice == "3":
            # look up password
            try:
                self.look_up()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt

        elif choice == "4":
            # delete a password
            try: 
                self.delete_one()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt

        elif choice == "5":
            # delete all passwords
            try:
                self.delete_all()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt
        
        else: 
            print(f'[red]{self.obj_.xmark_} Invalid option.[/red]')
            return self.begin_program()

    def menu_interface(self) -> None:
        """
        Menu interface

        Raises: 
            KeyboardInterrupt -- user interrupts
        """
        banner()
        print("[blue] 1) Add a password[/blue]")
        print("[blue] 2) Update informations[/blue]")
        print("[blue] 3) Look up passwords[/blue]")
        print("[red] 4) Delete a password (normal/master)[/red]")
        print("[red] 5) Delete all normal passwords[/red]")
        print("[red] 6) Exit the program[/red]")

        try:
            return str(input("\n └──Enter a choice: ")).strip()
        except KeyboardInterrupt: 
            raise KeyboardInterrupt
    
    def inform_data(self) -> tuple:
        """Inform the user datas 
        
        Raises: 
            KeyboardInterrupt -- user interrupts

        Returns
            platform [str] -- user platform to stored
            mail [str] -- email account
            password [str] - account's password
            url [str] - url of the platform
        """
        try: 
            platform = str(input("Enter the platform for which you want to store a password (ex. Google): ")).lower().strip().title()

            if platform.isnumeric() or platform.isspace():
                print(f"[red]{self.obj_.xmark_}Enter a valid answer[/red]")
                return self.__begin_informations()

            mail = str(input("Enter the email for this account: ")).lower().strip()
            url = str(input("Enter the URL of the website (ex. https://google.com): ")).lower().strip()

            if not url.startswith("http"):
                print(f"[red]{self.obj_.xmark_}Invalid URL. The URL must contain http:// or https:// in the beginning.[/red]")
                sleep(1)

                return self.__begin_informations()

            elif url.startswith("http"):
                try:
                    # Make a request in the URL gaved.
                    requests.get(url)

                except requests.ConnectionError:
                    # If the connection does not work, the URL is incorrect.
                    # Then the question will return
                    print(f"[red]{self.obj_.xmark_} Invalid URL.[/red]")
                    sleep(1)

                    return self.__begin_informations()

            want_gen = str(input(f"Do you want to generate a password for {platform}? (Y/n): ")).lower().strip()
            # Generate a password for a platform.
            if want_gen == "exit":
                exit("[cyan]Thanks for using.[/cyan]")

            elif want_gen == "y":
                try:
                    password = self.__return_generated()
                except KeyboardInterrupt: 
                    raise KeyboardInterrupt

            elif want_gen == "n":
                password = getpass.getpass(prompt=f"Enter the password which you want to add for {platform} in the database: ").strip()

            else:
                print("[red]Enter a valid answer.[/red]")
                return self.__begin_informations()
            
            return (platform, mail, password, url)

        except KeyboardInterrupt:
            raise KeyboardInterrupt

    def __return_generated(self) -> str: 
        """Returns a generated password
        
        Returns:
            str -- A randomly generated password
        """

        generated_pass = self.db.generate_password()
        loop = str(input("Generate a new password? (Y/n): ")).lower().strip()
        if loop == "exit":
            exit('Thanks for using.')
        elif (loop == 'y') or (loop.strip() == ""):
            return self.__return_generated() # recursive call
        elif loop == 'n':
            return generated_pass
    
    def edit_password(self) -> None:
        """
        Edit stored informations 
        
        Raises 
            PermissionError -- No permission to use

        Returns 
            New SQLite system application.
        """
        try:
            self.db.stored_passwords()
        except PermissionError: 
            return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/red]")
        
        option = str(input("What do you want to change? (platform/email/password/url) ")).lower().strip()
        if option not in ['platform', 'email', 'password', 'url']: 
            print(f'[red]{self.obj_.xmark_} Enter a valid answer.[/red]\n')
            return self.edit_password()
        new = str(input(f"Enter the new {option} which you want add in the database: ")).strip()

        if option == "" or new == "": 
            print(f'[red]{self.obj_.xmark_} Inputs could not be empty.[/red]\n')
            return self.edit_password()

        if option == "url":
            if not new.startswith("http"):
                print(f"[red]\n {self.obj_.xmark_} The URL must contain http:// or https:// in the beginning.[/red]\n")
                sleep(1)
                return self.edit_password()

            elif new.startswith("http"):
                try:
                    # Make a HTTP request in the URL
                    requests.get(new)
                except requests.ConnectionError:
                    # If the connection does not work, the URL is incorrect.
                    # Then the question will return
                    print(f"[red]\n{self.obj_.xmark_} Invalid URL. Please try again.\n[/red]")
                    sleep(1)
                    return self.edit_password()

        id_opt = str(input(f"\nEnter the ID from the {option}: "))
        self.db.edit_password(new, option, id_opt)

    def look_up(self) -> None:
        """
        Look up password

        Raises 
            PermissionError -- No permission to use
            KeyboardInterrupt -- User Interrupts the program

        Returns 
            New SQLite system application.
        """ 
        try:
            try:
                self.db.stored_passwords()
            except PermissionError: 
                return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/red]")

            id_opt = str(input('Enter ID for the password you want to retrieve: ')).strip()
            self.db.look_up(id_opt)
        except KeyboardInterrupt: 
            raise KeyboardInterrupt

    def delete_one(self) -> None:
        """
        Delete a password
        
        Raises 
            PermissionError -- No permission to use
            KeyboardInterrupt -- User Interrupts the program

        Returns 
            A password deleted
        """
        try:
            self.db.stored_passwords()
        except PermissionError: 
            return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/red]")


        try:
            delete_pwd = str(input("Delete normal password or master password? (normal/master) ").lower().strip())

            if delete_pwd == "exit":
                exit("[cyan]Thanks for using.[/cyan]")
            elif delete_pwd == "":
                return self.delete_one()
            elif delete_pwd == "normal":
                id = str(input("Enter the ID of the password which you want delete: ")).strip()
                return self.db.delete_normal(id)
            elif delete_pwd == "master":
                print('[red]NOTE: If you delete the master password you will lost all your sensitives data and will be logged out[/red]')
                confirm = str(input("Are you sure you want to delete the master password? (Y/n) ")).strip().lower()

                if confirm == "y":
                    self.db.delete_master()
                    sleep(1)
                    print("[green]Done. All passwods including the master password were deleted with success.[/green]")
                    sleep(1)
                    print('[red]Now you will be logged out.[/red]')
                    print('[cyan]Thanks for using.[/cyan]')
                    exit(1)
                
                elif confirm != "n": 
                    return

        except KeyboardInterrupt: 
            raise KeyboardInterrupt

    def delete_all(self) -> None: 
        """
        Delete all stored passwords

        Raises 
            PermissionError -- No permission to use
            KeyboardInterrupt -- User Interrupts the program
        
        Returns 
            Database file empty
        """
        try:
            self.db.stored_passwords()
        except PermissionError: 
            return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/red]")

        try:
            confirm = str(input("Are you sure you want to delete all normal passwords? (Y/n) "))
            if confirm == "y".strip().lower():
                self.db.delete_all()
            elif confirm == "exit".strip().lower():
                print("[cyan]Thanks for using.[/cyan]")
                exit(1)
            elif confirm == "".strip().lower():
                return self.delete_all()
        except KeyboardInterrupt: 
            raise KeyboardInterrupt
