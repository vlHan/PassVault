from modules import *

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class Encryption:
    def __init__(self) -> None:
        """
        Encryption Class 
        """
        self.encoding = 'utf-8'

    def encrypt(self, pssw: str, key: str) -> tuple:
        """
        Encrypt using master password as the key

        Arguments
            pssw [str] -- password to be encrypted
            key [str] -- a master password to encrypt and decrypt

        Return 
            [str] initial value and the cyphertext in base64 (concatenate string)
        """

        pssw = pssw.encode(self.encoding)
        key = key.encode(self.encoding)
        cipher = AES.new(key, AES.MODE_CBC)
        concatenate_bytes = cipher.encrypt(pad(pssw, AES.block_size))

        iv = b64encode(cipher.iv).decode(self.encoding)
        concatenate = b64encode(concatenate_bytes).decode(self.encoding)

        return (iv, concatenate)

    def decrypt(self, initial_value: str, ciphertext: str, key: str) -> str:
        """
        Decrypt data using master password as the key.

        Arguments
            initial_value [str] -- the value to pass to base64
            ciphertext [str] -- to encrypt and decrypt
            key [str] -- a master password to encrypt and decrypt

        Returns 
            [str] The cypher text decrypted      
        """
        initial_value = b64decode(initial_value)
        concatenate = b64decode(ciphertext)
        key = key.encode(self.encoding)
        cipher = AES.new(key, AES.MODE_CBC, initial_value)

        return unpad(cipher.decrypt(concatenate), AES.block_size)
