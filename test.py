import re
regex = r'[0-9]{3}\.[0-9]{3}\.[0-9]{4}'

print(re.findall(regex, "jelkjalskdjf(756.837.1872jklejlkjasdf083-876jelkajslkdf"))