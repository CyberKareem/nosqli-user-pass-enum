NoSQLi User/Pass Enumeration python script using Regex Injection.

This script performs parameter enumeration using regex injection for web forms. It allows you to enumerate a specific parameter (e.g., username or password) on a web form by exploiting regex injection vulnerabilities. It sends requests to the target URL with different payloads to determine if the parameter can be leaked through the application's response.
In this simplified version, I've cleaned up the code, extracted functionalities into functions for better readability, and eliminated redundant checks. 
I've also consolidated the repetitive code for building payloads into a separate function. 
Inspired by https://github.com/an0nlk/Nosql-MongoDB-injection-username-password-enumeration/blob/master/README.md

I have enhanced the script by incorporating the following improvements:

Adding comments to explain the functionality of important parts of the code.
Using more descriptive variable names for better readability.
Handling exceptions and error messages more gracefully.
Using f-strings for string formatting (available in Python 3.6 and above) for better code readability.
Streamlining the argument parsing and reducing code duplication.

The script will only display the found usernames and passwords. Additionally, it will provide a message if no username or password is found during the enumeration process. 

Prerequisites:

- Python 3.x
- The following Python libraries:
    - string
    - requests
    - argparse
    - sys
    - colorama

How to Use:
Clone the repository or download the script.

Install the required Python libraries using pip:

pip install requests argparse colorama

Run the script with the following command-line arguments:

python parameter_enumeration.py -u URL -up USERNAME_PARAM -pp PASSWORD_PARAM -ep ENUM_PARAM [-op OTHER_PARAMS] [-m METHOD]

-u or --url: The URL of the form to test (required).
-up or --username-parameter: The parameter name of the username (required).
-pp or --password-parameter: The parameter name of the password (required).
-ep or --enum-parameter: The parameter that needs to be enumerated (required).
-op or --other-parameters: Other parameters with their values (optional).
-m or --method: Method of the form (GET or POST) (optional, default is POST).

Output
The script will display the following output:
- Patterns found during the enumeration process.
- The username/password parameter(s) found.
- A message if no username/password parameter is found.

Disclaimer
This script is intended for educational and testing purposes only. 
Do not use it against any website or application without the proper authorization. 
Unauthorized use may violate applicable laws and regulations. 
The developer of this script is not responsible for any misuse or illegal activities. Use it responsibly and at your own risk.



