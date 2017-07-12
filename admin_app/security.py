# coding: utf8

import re
import uuid
import gluon.contrib.aes as AES
import threading
import os
import base64


class Enc:
    def __init__(self, key=''):
        self.key = ''
        self.set_key(key)

    def get_key(self):
        if self.key == '':
            # Ensure we have a key set
            self.set_key()
        return self.key

    def set_key(self, key=''):
        if key == '':
            # Guid w no - should be 32 bytes
            key = str(uuid.uuid4()).replace('-', '')
        # Make sure the key is 32 bytes
        key = Enc.pad(key[:32])
        self.key = key

    @staticmethod
    def natural_key(string_):
        return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

    @staticmethod
    def fast_urandom16(urandom=[], locker=threading.RLock()):
        """
        this is 4x faster than calling os.urandom(16) and prevents
        the "too many files open" issue with concurrent access to os.urandom()
        """
        try:
            return urandom.pop()
        except IndexError:
            try:
                locker.acquire()
                ur = os.urandom(16 * 1024)
                urandom += [ur[i:i + 16] for i in xrange(16, 1024 * 16, 16)]
                return ur[0:16]
            finally:
                locker.release()

    @staticmethod
    def pad(s, n=32, pad_char=' '):
        while (len(s) % n) != 0:
            s += pad_char
        return s

    @staticmethod
    def aes_new(key, iv=None):
        """ Returns an AES cipher object and random IV if None specified """
        if iv is None:
            iv = Enc.fast_urandom16()

        return AES.new(str(key), AES.MODE_CBC, iv), iv

    def encrypt(self, data):
        key = self.get_key()
        cipher, iv = Enc.aes_new(key)
        encrypted_data = iv + cipher.encrypt(Enc.pad(data))
        return base64.urlsafe_b64encode(encrypted_data)

    def decrypt(self, data):
        key = self.get_key()
        if data is None:
            data = ""
        # Make sure data is ascii
        data = str(data)
        data = base64.urlsafe_b64decode(data)
        iv, data = data[:16], data[16:]
        cipher, _ = Enc.aes_new(key, iv=iv)
        data = cipher.decrypt(data)
        data = data.rstrip(' ')
        return data
