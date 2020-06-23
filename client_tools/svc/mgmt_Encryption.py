
import os

import pyaes as AES
import threading
import base64

from color import p

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
            urandom += [ur[i:i + 16] for i in range(16, 1024 * 16, 16)]
            return ur[0:16]
        finally:
            locker.release()


def pad(s, n=32, padchar=' '):
    if len(s) == 0:
        # Handle empty value - pad it out w empty data
        s += padchar * n
        return s
    while ((len(s) % n) != 0):
        s += padchar
    #pad_len = len(s) % 32 # How many characters do we need to pad out to a multiple of 32
    #if (pad_len != 0):
    #    #return s + (32 - len(s) % 32) * padchar
    #    return s + (
    return s


def AES_new(key, iv=None):
    """ Returns an AES cipher object and random IV if None specified """
    if iv is None:
        iv = fast_urandom16()

    # return AES.new(key, AES.MODE_CBC, IV), IV
    # Util.aes = pyaes.AESModeOfOperationCBC(key, iv = iv)
    # plaintext = "TextMustBe16Byte"
    # ciphertext = aes.encrypt(plaintext)
    if not isinstance(key, bytes):
            key = key.encode('utf-8')
    return AES.AESModeOfOperationOFB(key, iv = iv), iv

class Encryption:
    @staticmethod
    def encrypt(data, key):
        key = pad(key[:32])
        cipher, iv = AES_new(key)
        encrypted_data = iv + cipher.encrypt(pad(data, 16))
        return base64.urlsafe_b64encode(encrypted_data)

    @staticmethod
    def decrypt(data, key):
        key = pad(key[:32])
        if data is None:
            data = ""
        try:
            data = base64.urlsafe_b64decode(data)
        except TypeError as ex:
            # Don't let error blow things up
            pass
        iv, data = data[:16], data[16:]
        try:
            cipher, _ = AES_new(key, iv=iv)
        except:
            # bad IV = bad data
            return "" # data
        try:
            data = cipher.decrypt(data)
        except:
            # Don't let error blow things up
            return ""
            pass

        if isinstance(data, bytes):
            #p("is bytes")
            try:
                data = data.decode('utf-8')
                #p("f")
            except:
                p("err decoding encrypted data as utf-8")
                try:
                    data = data.decode('ascii')
                except:
                    p("err decoding encrypted data as ascii", log_level=5)
                    try:
                        data = data.decode('latin-1')
                    except:
                        p("err decoding encrypted data as latin-1 - returning raw data",
                            log_level=4)
                        data = str(data)
        data = data.rstrip(' ')
        return data