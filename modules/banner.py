# -*- coding: utf-8 -*-

from colorama import Fore, Style

__author__ = "vlHan"
__version__ = "V1.2"


def banner() -> None:
    """
    The banner for the system.
    """
    print(f"""{Fore.CYAN}
       ___             _   __          ____ 
      / _ \___ ____ __| | / /__ ___ __/ / /_
     / ___/ _ `(_-<(_-< |/ / _ `/ // / / __/
    /_/   \_,_/___/___/___/\_,_/\_,_/_/\__/ 
                                            
    author: {__author__}
    version: {__version__}
    GitHub: https://github.com/vlHan/PassVault
    
    {Fore.MAGENTA}*Enter 'exit' or 'Ctrl + C' at any point to exit.*\n{Style.RESET_ALL}""")
