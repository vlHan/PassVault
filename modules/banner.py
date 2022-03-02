from rich import print

__author__ = "vlHan"
__version__ = "V1.5"
__license__ = "MIT"

def banner() -> None:
    print(f"""[cyan]
       ___             _   __          ____ 
      / _ \___ ____ __| | / /__ ___ __/ / /_
     / ___/ _ `(_-<(_-< |/ / _ `/ // / / __/
    /_/   \_,_/___/___/___/\_,_/\_,_/_/\__/ 
                                            
    author: {__author__}
    version: {__version__}
    GitHub: https://github.com/vlHan/PassVault
    
    [/cyan][magenta]*Enter 'Ctrl + C' at any point to exit.*[/magenta]\n""")
