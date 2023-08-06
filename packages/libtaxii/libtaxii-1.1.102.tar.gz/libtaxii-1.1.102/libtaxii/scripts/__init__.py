# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import argparse
import libtaxii.clients as tc

class ProxyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Turns the 'None' string argument into the None object
        that the API expects.
        """
        if option_string == "--proxy" and values == "None":
            values = None
        
        setattr(namespace, self.dest, values)

def create_client(args):
    client = tc.HttpClient()
    client.setUseHttps(args.https)
    client.setProxy(args.proxy)
    tls = (args.cert is not None and args.key is not None)
    basic = (args.username is not None and args.password is not None)
    if tls and basic:
        client.setAuthType(tc.HttpClient.AUTH_CERT_BASIC)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert, 'username': args.username, 'password': args.password})
    elif tls:
        client.setAuthType(tc.HttpClient.AUTH_CERT)
        client.setAuthCredentials({'key_file': args.key, 'cert_file': args.cert})
    elif basic:
        client.setAuthType(tc.HttpClient.AUTH_BASIC)
        client.setAuthCredentials({'username': args.username, 'password': args.password})
    
    return client

def get_base_parser(parser_description, path="/services/discovery/"):
    """
    Parser things common to all scripts. Parsers for specific TAXII Services should 
    add their own arguments.
    """
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument("--host", dest="host", default="taxiitest.mitre.org", help="Host where the Discovery Service is hosted. Defaults to taxiitest.mitre.org.")
    parser.add_argument("--port", dest="port", default="80", type=int, help="Port where the Discovery Service is hosted. Defaults to 80.")
    parser.add_argument("--path", dest="path", default=path, help="Path where the Discovery Service is hosted. Defaults to %s" % path)
    parser.add_argument("--https", dest="https", default=False, type=bool, help="Whether or not to use HTTPS. Defaults to False")
    parser.add_argument("--cert", dest="cert", default=None, help="The file location of the certificate to use. Defaults to None.")
    parser.add_argument("--key", dest="key", default=None, help="The file location of the private key to use. Defaults to None.")
    parser.add_argument("--username", dest="username", default=None, help="The username to authenticate with. Defaults to None.")
    parser.add_argument("--pass", dest="password", default=None, help="The password to authenticate with. Defaults to None.")
    parser.add_argument("--proxy", dest="proxy", action=ProxyAction, default='noproxy', 
                        help="A proxy to use (e.g., http://example.com:80/), or None to not use any proxy. Omit this to use the system proxy.")
    
    return parser
