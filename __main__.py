# -*- coding: utf-8 -*-
try:
    import sqlite3
    import Crypto
    import requests

except ImportError:
    import os
    os.system("pip install -r requirements.txt")

from modules.main import *

if __name__ == '__main__':
    Manager().main()
