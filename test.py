import re
print(re.search(r' N.', "240 N. Villa Ave.Willows,CA95677United States", re.IGNORECASE).group())