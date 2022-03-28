from modules import *

import requests
import getpass

from time import sleep
from sys import exit


class Menu:
    """
    Menu class to grab informations from the user

    Arguments
        master_pw {str} -- master password
        obj {Class} -- create instance of a class
    """
    def __init__(self, master_pw: str, obj) -> None:
        self.obj_ = obj
        self.db = Database(master_pw, obj)

    def begin_program(self) -> str:
        """
        Beginning of the program

        Raises:
            KeyboardInterrupt -- user interrupts

        Returns
            Informations to store in the database  
        """
        banner()
        print("[blue] 1) Add a password[/]"
        "\n[blue] 2) Update informations[/]"
        "\n[blue] 3) Look up passwords[/]"
        "\n[red] 4) Delete a password[/]"
        "\n[red] 5) Delete all normal passwords[/]"
        "\n[red] 6) Delete all data[/]"
        "\n[red] 7) Exit the program[/]")

        try:
            choice = str(input("\n └──Enter a choice: ")).strip()

            if choice in ["7", "exit"]:
                # Exit
                print("[cyan]Thanks for using.[/cyan]")
                exit(0)
                
            elif choice == "1":
                # add password
                platform, mail, password, url = self.add_data()
                self.db.save_password(platform, mail, password, url)

            elif choice == "2":
                # edit informations
                self.edit_password()

            elif choice == "3":
                # look up password
                self.look_up()

            elif choice == "4":
                # delete a password
                self.delete_one_password()

            elif choice == "5":
                # delete all normal passwords
                self.delete_all_passwords()
            
            elif choice == "6": 
                # delete all passwords including master password
                self.delete_all_data()
            
            else: 
                print(f'[red]{self.obj_.xmark_} Invalid option.[/]')
                return self.begin_program()
        
        except EOFError: 
            raise KeyboardInterrupt

    def add_data(self) -> tuple:
        """
        Inform the user datas 
        
        Raises: 
            KeyboardInterrupt -- user interrupts

        Returns
            platform {str} -- user platform to stored
            mail {str} -- email account
            password {str} - account's password
            url {str} - url of the platform
        """
        try: 
            platform = str(input("Enter the platform for which you want to store a password (ex. Google): ")).lower().strip().title()

            if platform.isnumeric() or platform.isspace():
                print(f"[red]{self.obj_.xmark_}Enter a valid answer[/]")
                return self.add_data()

            mail = str(input("Enter the email for this account: ")).lower().strip()
            url = str(input("Enter the URL of the website (ex. https://google.com): ")).lower().strip()

            self.httpverify(url)

            want_gen = str(input(f"Do you want to generate a password for {platform}? (Y/n): ")).lower().strip()

            if want_gen == "y":
                password = self.__return_generated()
            elif want_gen == "n":
                password = getpass.getpass(prompt=f"Enter the password which you want to add for {platform} in the database: ").strip()
            else:
                print("[red]Enter a valid answer.[/]")
                return self.add_data()
            
            return (platform, mail, password, url)

        except KeyboardInterrupt:
            raise KeyboardInterrupt

    def httpverify(self, url):
        """
        Verify the URL by sending HTTP request

        Arguments
            url {str} -- the URL of the platform

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

    def __return_generated(self) -> str:
        """Returns a generated password
        
        Returns:
            str -- A randomly generated password
        """
        try:
            generated_pass = self.db.generate_password()
            loop = str(input("Generate a new password? (Y/n): ")).lower().strip()
            if (loop == 'y') or (loop.strip() == ""):
                return self.__return_generated() # recursive call
            elif loop == 'n':
                return generated_pass
        except KeyboardInterrupt: 
            raise KeyboardInterrupt
    
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
        try: 
            option = str(input("\nWhat do you want to change? (platform/email/password/url) ")).lower().strip()
            if option not in ['platform', 'email', 'password', 'url']: 
                print(f'[red]{self.obj_.xmark_} Enter a valid answer.[/]\n')
                return self.edit_password()

            new = str(input(f"Enter the new {option} which you want add: ")).strip()
            if option == "" or new == "": 
                print(f'[red]{self.obj_.xmark_} Inputs could not be empty.[/]\n')
                return self.edit_password()
            elif option == "url":
                self.httpverify(new)

            id_opt = str(input(f"\nEnter the ID from the {option}: "))
            self.db.edit_password(new, option, id_opt)
        except KeyboardInterrupt: 
            raise KeyboardInterrupt

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
            id_opt = str(input("Enter the ID of the password which you want delete: ")).strip()
            return self.db.delete_one_password(id_opt)

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
            confirm = str(input("\nAre you sure you want to delete all passwords? (Y/n) ")).strip().lower()
            if confirm == "y":
                self.db.delete_all_passwords()
            elif confirm == 'n':
                self.obj_.exit
            elif confirm == "":
                return self.delete_all_passwords()
        except KeyboardInterrupt: 
            raise KeyboardInterrupt

    def delete_all_data(self):
        """
        Delete all data including master password
        """
        print('[red]If you delete the master password you will lost all data[/]')
        try:
            confirm = str(input("Are you sure you want to delete the master password? (Y/n) ")).strip().lower()

            if confirm == "y":
                self.db.delete_all_data()
                print(f"[green]{self.obj_.checkmark_} All passwords deleted successfully.[/green]")
                exit(0)
            elif confirm == 'n':
                print("[red]Cancelling...[/]")
                return self.begin_program()
            elif confirm == "exit":
                self.obj_.exit_program()
            
        except KeyboardInterrupt: 
            raise KeyboardInterrupt
