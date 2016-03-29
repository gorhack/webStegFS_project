#!/usr/bin/env python3

"""
The list of possible https and http proxies to use with `sendspace`. Proxies are necessary on the DREN at USMA.
The DREN blocks many file-sharing websites, such as `sendspace`.

Free US proxies:

- ``http://165.139.149.169:3128``
- ``https://165.139.149.169:3128``
"""

proxies = {'https': 'https://165.139.149.169:3128',
           'http': 'http://165.139.149.169:3128'}
