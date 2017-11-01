from Crypto.Cipher import AES
from Crypto import Random
import base64
import sys
import os
import random

BS = 16
pad = lambda s: s + (BS - len(s)%BS) * chr(BS - len(s) % BS)

class client_auth:
    def __init__(self):
        super(client_auth, self).__init__()

    def encryptText(self, plainText, Key):
        plainText = pad(plainText)
        iv = Random.new().read(AES.block_size)
        secret_key = Key;
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)

        return base64.b64encode(iv + cipher.encrypt(plainText))
