# -*- coding: utf-8 -*-
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

    Manager().main()
