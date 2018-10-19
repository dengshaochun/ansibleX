#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/18 17:39
# @Author  : Dengsc
# @Site    : 
# @File    : encrypt.py
# @Software: PyCharm

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from django.conf import settings


class PrpCrypt(object):
    def __init__(self, key=settings.AES_SECRET_KEY):
        key = str(key)[:16]
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        text = text.encode('utf-8')
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + ('\0' * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            text = text + ('\0' * add).encode('utf-8')
        ciphertext = cryptor.encrypt(text)

        return b2a_hex(ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip('\0')
