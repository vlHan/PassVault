# -*- coding: utf-8 -*-

from colorama import Fore, Style

__author__ = "vlHan"
__version__ = "V1.1"


def banner() -> None:
    """
    The banner for the system.
    """
    print(Fore.CYAN + f"""
       ___             _   __          ____ 
      / _ \___ ____ __| | / /__ ___ __/ / /_
     / ___/ _ `(_-<(_-< |/ / _ `/ // / / __/
    /_/   \_,_/___/___/___/\_,_/\_,_/_/\__/ 
                                            
    author: {__author__}
    version: {__version__}
    GitHub: https://github.com/vlHan/PassVault\n""" + Style.RESET_ALL)

