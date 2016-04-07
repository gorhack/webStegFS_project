import argparse
from webStegFS import console

default_proxies = {'https': 'https://165.139.149.169:3128',
                   'http': 'http://165.139.149.169:3128'}


def proxy_test(proxyL):
    import requests
    try:
        r = requests.get('https://google.com', timeout=5)
        assert(r.status_code is 200)
    except:
        print("Cannot connect to Internet or Google is down!")
        return
    # now test proxy functionality
    try:
        # Add something in here later to actually test proxy with given file
        # store. Use google for now.
        r = requests.get('http://www.sendspace.com', proxies=proxyL, timeout=5)
        print(r)
        assert(r.status_code == 200)
    except:
        print("Given (or default) proxy is down, or took too long to respond")
        return
    else:
        print("Proxy is operational")
        return proxyL


def proxy_parser(proxyString=None):
    if proxyString is None:
        return proxy_test(default_proxies)
    proxy = proxyString.split(':')[0]
    port = proxyString.split(':')[1]
    import ipaddress
    try:
        print(ipaddress.ip_address(proxy))
        assert(int(port) > 0 & int(port) < 65536)
    except:
        print("Invalid IP address for proxy. Enter the proxy again.")
        return
    proxDict = {'https': 'https'+proxy+':'+port,
                'http': 'http'+proxy+':'+port}
    return proxDict  # proxy_test(proxDict)


def main():
    parser = argparse.ArgumentParser(description="Calls the main function of" +
                                     " WebStegFS")
    parser.add_argument('url', type=str, default='', nargs='?',
                        help='Specify the url to load a filesystem from')
    parser.add_argument('-c', dest='cmdloop', default=False,
                        action='store_true', help='Use the command loop to' +
                        ' access the filesystem')
    parser.add_argument('-d', dest='debug', default=False, action='store_true',
                        help='Enable debug print statements. For dev use')
    parser.add_argument('-w', dest='website', type=str, default='sendspace',
                        help='Use alternate online file stores from command' +
                        ' line')
    parser.add_argument('-p', dest="proxy", type=str, default='noproxy',
                        nargs='?', help='Use a specific proxy to access the' +
                        ' web file store. There is a default if none is ' +
                        'provided. Format is simply an IP address with port' +
                        ' at the end (e.x. 1.2.3.4:8080)')
    parser.add_argument('-e', dest='encryption', type=str, default='noencrypt',
                        nargs='?', help='Use a specific encryption.')
    parser.add_argument('-m', dest="mountpoint", type=str,
                        default='covertMount', help='Specify a foldername' +
                        ' to mount the FUSE module at')
    parser.add_argument('-s', dest='steganography', default='LSBsteg',
                        nargs='?', help='Use an alternate steganography' +
                        '  class for encoding in images')

    args = parser.parse_args()
    print(args)

    run = True
    if args.proxy == 'noproxy':
        proxy = None
    else:
        proxy = proxy_parser(args.proxy)
        if proxy is None:
            run = False

    if args.encryption == 'noencrypt':
        encrypt = None
    else:
        if args.encryption is None:
            args.encryption = 'xor'  # xor is the default encryption class.
            # In the absence of an argument for -e, xor is used.
        encrypt = args.encryption

    if run:
        cons = console.Console(args.website, args.steganography,
                               encrypt, args.mountpoint, args.url,
                               proxy, args.cmdloop, args.debug)

        if args.url:
            cons.loadfs()
        if args.cmdloop:
            cons.cmdloop()
        else:
            cons.do_mount(None)

if __name__ == '__main__':
    main()
