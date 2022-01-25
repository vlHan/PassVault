# -*- coding: utf-8 -*-
from sqlite3 import DatabaseError


try:
    import Crypto
    import requests
    import colorama
except ImportError:
    import os
    os.system("pip install -r requirements.txt")
    print()

if __name__ == '__main__':
    from modules import *
    
    Manager(DataBase()).main()
