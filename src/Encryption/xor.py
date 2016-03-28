#!/usr/bin/env python3


class XOR(object):
    """
    The XOR class uses a simple XOR cipher to obfuscate data with a key.
    """

    def encrypt(self, key, data):
        """
        The encrypt method encrypts the provided data with a key.
        The method takes a key as an integer between 0 and 256 and
        the data as a bytearray object.
        The method returns an encrypted bytearray object.
        """
        return bytearray(x ^ key for x in data)

    def decrypt(self, key, data):
        """
        The decrypt method decrypts the provided data with a key.
        Since XOR is reversible with the same key, decrypt is the
        same as encrypt.
        The method takes a key as an integer between 0 and 256 and
        the data as a bytearray object.
        The method returns an encrypted bytearray object.
        """
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
        print("key must be integer [0-256], using key = 0.")
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
