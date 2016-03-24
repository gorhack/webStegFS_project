#!/usr/bin/env python3

"""@package xor

Documentation for the xor module.
"""


class XOR(object):
    """
    The XOR class uses a simple XOR to obfuscate data with a key.
    """

    def encrypt(self, key, data):
        return bytearray(x ^ key for x in data)

    def decrypt(self, key, data):
        return self.encrypt(key, data)

if __name__ == '__main__':
    # python3 -m src.Encryption.xor [key] [data]
    # data as string for easiest use

    import sys
    xor = XOR()
    k = 0
    try:
        k = int(sys.argv[1])
    except ValueError:
        print("key must be integer [0-255], using key = 0.")
    d = bytearray(sys.argv[2].encode())

    enc_data = xor.encrypt(k, d)
    print("Encrypted data: {}".format(enc_data))

    dec_data = xor.decrypt(k, enc_data)
    print("Decrypted data: {}".format(dec_data))

    if d == dec_data:
        print("Encryption/Decryption success!")
    else:
        print("Encryption/Decryption failed." +
              "data: {} + \n decrypted data: {}".format(d, dec_data))
