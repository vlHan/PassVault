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
        obj [Class] -- create instance of a class
    """
    def __init__(self, master_pw: str, obj) -> None:
        self.obj_ = obj
        self.db = DataConnect(master_pw, obj)

    def begin_program(self) -> str:
        """
        Beginning of the program

        Raises: 
            KeyboardInterrupt -- user interrupts

        Returns
            Informations to store in the database  
        """
        choice = self.menu_interface()
        if choice in ["7", "exit"]:
            # Exit
            print("[cyan]Thanks for using.[/cyan]")
            exit(0)

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
                self.delete_one_password()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt

        elif choice == "5":
            # delete all normal passwords
            try:
                self.delete_all_passwords()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt
        
        elif choice == "6": 
            # delete all passwords including master password
            try:
                self.delete_all_data()
            except KeyboardInterrupt: 
                raise KeyboardInterrupt
        
        else: 
            print(f'[red]{self.obj_.xmark_} Invalid option.[/]')
            return self.begin_program()

    def menu_interface(self) -> None:
        """
        Menu interface

        Raises: 
            KeyboardInterrupt -- user interrupts
        """
        banner()
        print("[blue] 1) Add a password[/]"
        "\n[blue] 2) Update informations[/]"
        "\n[blue] 3) Look up passwords[/]"
        "\n[red] 4) Delete a password[/]"
        "\n[red] 5) Delete all passwords[/]"
        "\n[red] 6) Delete all normal data[/]"
        "\n[red] 7) Exit the program[/]")

        try:
            return str(input("\n └──Enter a choice: ")).strip()
        except KeyboardInterrupt: 
            raise KeyboardInterrupt
    
    def httpverify(self, url):
        """
        Verify the URL by sending HTTP request

        Arguments
            url [str] -- the URL of the platform

        Returns 
            If the URl is correct
        """ 
        if not url.startswith("http"):
            print(f"[red]{self.obj_.xmark_} Invalid URL. The URL must contain http:// or https:// [/]")
            sleep(1)

            return self.inform_data()

        elif url.startswith("http"):
            try:
                requests.get(url)
            except requests.ConnectionError:
                print(f"[red]{self.obj_.xmark_} Invalid URL.[/]")

                return self.inform_data()

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
                print(f"[red]{self.obj_.xmark_}Enter a valid answer[/]")
                return self.inform_data()

            mail = str(input("Enter the email for this account: ")).lower().strip()
            url = str(input("Enter the URL of the website (ex. https://google.com): ")).lower().strip()

            self.httpverify(url)

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
                print("[red]Enter a valid answer.[/]")
                return self.inform_data()
            
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
            return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/]")
        
        option = str(input("\nWhat do you want to change? (platform/email/password/url) ")).lower().strip()
        if option not in ['platform', 'email', 'password', 'url']: 
            print(f'[red]{self.obj_.xmark_} Enter a valid answer.[/]\n')
            return self.edit_password()

        new = str(input(f"Enter the new {option} which you want add: ")).strip()
        if option == "" or new == "": 
            print(f'[red]{self.obj_.xmark_} Inputs could not be empty.[/]\n')
            return self.edit_password()

        if option == "url":
            self.httpverify(new)

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
                return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/]")

            id_opt = str(input('\nEnter ID for the password you want to retrieve: ')).strip()
            print(self.db.look_up(id_opt))
        except KeyboardInterrupt: 
            raise KeyboardInterrupt

    def delete_one_password(self) -> None:
        """
        Delete a password normal or master
        
        Raises 
            PermissionError -- No permission to use
            KeyboardInterrupt -- User Interrupts the program

        Returns 
            A password deleted
        """

        try:
            try:
                self.db.stored_passwords()
            except PermissionError: 
                return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/]")
            id = str(input("Enter the ID of the password which you want delete: ")).strip()
            return self.db.delete_one_password(id)

        except KeyboardInterrupt: 
            raise KeyboardInterrupt

    def delete_all_passwords(self) -> None: 
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
            return print(f"[red]{self.obj_.xmark_} The database is empty. Try adding a password.[/]")

        try:
            confirm = str(input("\nAre you sure you want to delete all passwords? (Y/n) "))
            if confirm == "y".strip().lower():
                try:
                    entered_master = getpass.getpass("Enter your master password to delete all stored passwords: ").strip()
                    self.db.delete_all_passwords(entered_master)
                except KeyboardInterrupt: 
                    raise KeyboardInterrupt
            elif confirm is ['exit' or 'n']:
                self.obj_.exit
            elif confirm == "".strip().lower():
                return self.delete_all_passwords()
        except KeyboardInterrupt: 
            raise KeyboardInterrupt

    def delete_all_data(self):
        """
        Delete all data including master password
        """
        print('[red]If you delete the master password you will lost all data[/]')
        confirm = str(input("Are you sure you want to delete the master password? (Y/n) ")).strip().lower()

        if confirm == "y":
            self.db.delete_all_data()
            print(f"[green]{self.obj_.checkmark_} All passwords deleted successfully.[/green]")
            exit(0)
        elif confirm.lower().strip() == 'n':
            print("[red]Cancelling...[/]")
            return self.begin_program()
        elif confirm.lower().strip() == "exit":
            self.obj_.exit_program()
        elif confirm.strip() == "":
            return self.delete_all_data()
