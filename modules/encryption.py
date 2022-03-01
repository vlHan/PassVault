from modules import *

from base64 import b64encode, b64decode
from Crypto.Cipher import AES


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
            pssw {str} -- password to be encrypted
            key {str} -- a master password to encrypt and decrypt

        Return 
            {str} tag, nonce and the cyphertext in base64 (concatenate string)
        """

        pssw = pssw.encode(self.encoding)
        key = key.encode(self.encoding)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(pssw)

        return b64encode(tag).decode('utf-8'), b64encode(cipher.nonce).decode('utf-8'), b64encode(ciphertext).decode('utf-8')

    def decrypt(self, tag: str, nonce: str, ciphertext: str, key: str) -> str:
        """
        Decrypt data using master password as the key.

        Arguments
            tag {str} -- the value to decrypt the password
            nonce {str} -- the value to decrypt the password
            ciphertext {str} -- to encrypt and decrypt
            key {str} -- a master password to encrypt and decrypt

        Returns 
            {str} The cypher text decrypted      
        """
        tag = b64decode(tag)
        ciphertext = b64decode(ciphertext)
        key = key.encode(self.encoding)
        cipher = AES.new(key, AES.MODE_GCM, nonce=b64decode(nonce))
        decoded = cipher.decrypt_and_verify(ciphertext, tag)
        return decoded.decode()
