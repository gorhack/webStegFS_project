#!/usr/bin/env python3

"""@package xor

Documentation for the xor module.
"""


class XOR(object):
    """
    The XOR class uses a simple XOR to obfuscate data with a key.
    """

    def encrypt(self, key, data):
        return bytearray(x ^ key for x in message)

    def decrypt(self, key, data):
        return encrypt(key, data)
