#!/usr/bin/env python3


def ssl_proxy():
    """
    The SSL proxy is a free US proxy https://165.139.149.169:3128.
    """
    return 'https://165.139.149.169:3128'


def proxy():
    """
    Proxy without SSL.
    """
    return 'http://165.139.149.169:3128'


proxies = {'https': ssl_proxy(),
           'http': proxy()}
