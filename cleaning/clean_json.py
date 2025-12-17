import json
import argparse
import re

# Define the parser
parser = argparse.ArgumentParser(description='Script to clean a dataset')

# Declare an argument (`--algo`), saying that the 
# corresponding value should be stored in the `algo` 
# field, and using a default value if the argument 
# isn't given
parser.add_argument('--file', action="store", dest='location', default=0)
parser.add_argument('-f', action="store", dest='location', default=0)

parser.add_argument('--result', action="store", dest='result_location', default=0)
parser.add_argument('-r', action="store", dest='result_location', default=0)

# Now, parse the command line arguments and store the 
# values in the `args` variable
args = parser.parse_args()


def clean_phone_number(number: str) -> str:
    numbers: list[str] = re.findall(r'\d+', number)
    return "(" + numbers[0] + ") " + numbers[1] + " " + numbers[2]

def clean_address(address: str) -> str:
    address_regex_first = r'[0-9]+ (((n\.?)|(s\.?)|(e\.?)|(w\.?)|(north)|(south)|(east)|(west)) )?[a-zA-Z]+ ((street)|(str\.?)|(avenue)|(ave\.?)|(road)|(rd\.?)|(boulevard)|(blvd\.?)|(drive)|(dr\.?)|(lane)|(ln\.?))'
    
    first_line_search = re.search(address_regex_first, address, re.IGNORECASE)
        
    if isinstance(first_line_search, re.Match):
        # get first line of address
        cleaned_address = first_line_search.group()
        
        # remove first line of address from address, as well as the substring preceding it
        regex_first = r'.*?' + cleaned_address
        address = re.sub(regex_first, "", address)
                        
        zip_code = re.findall(r'[0-9]+', address)[0]
        address_second_line: str = address.split(zip_code)[0]
        address_second_line += zip_code
        address_second_line = address_second_line.strip()
        
        split_second_line = address_second_line.split()
        if len(split_second_line) > 2:  # 3 or more substrings when split by spaces, address is most likely split up properly with spaces
            address_second_line_cleaned = split_second_line.pop()
            address_second_line_cleaned = split_second_line.pop() + " " + address_second_line_cleaned
            city_name = " ".join(split_second_line)
            # if no comma at end, append comma
            if city_name[-1] != ",":
                city_name += ","
            city_name += " "
            address_second_line_cleaned = city_name + address_second_line_cleaned
            return cleaned_address + "  " + address_second_line_cleaned
        
        else:
            # start with the zip code which is already known
            address_second_line_cleaned = zip_code
            # remove zip_code
            second_line: str = address_second_line.split(zip_code)[0]
            # get state
            address_second_line_cleaned = second_line.split(",")[-1] + " " + address_second_line_cleaned
            # get city
            city_name = second_line.split(",")[0]
            address_second_line_cleaned = re.sub( r"([A-Z])", r" \1", city_name) + " " + address_second_line_cleaned
            return cleaned_address + "  " + address_second_line_cleaned
                    
    # if no match found, then address is a bad address
    else:
        return "Unknown"

def clean_data():

    cleaned_data_dictionary = {
        "county_resources": [],
    }

    with open(args.location) as f:
        d: dict = json.load(f)

        for result in d["results"]:
            
            data_dict = {}
            
            data_dict["county"] = result["county"]
            data_dict["department_name"] = result["department_name"]
            data_dict["population"] = result["population"]
            data_dict["link"] = result["url"]
            
            data_dict["phone_numbers"] = []
            data_dict["facility_names"] = []
            data_dict["addresses"] = []
            
            for resource in result["resources"]:
                if resource["type"] == "phone_number":
                    data_dict["phone_numbers"].append(
                        {
                            "number": clean_phone_number(resource["value"]),
                            "tags": resource["tags"],
                        }
                    )
                elif resource["type"] == "facility_name":
                    data_dict["facility_names"].append(
                        {
                            "name": resource["value"],
                            "tags": resource["tags"],
                        }
                    )
                elif resource["type"] == "address":
                    data_dict["addresses"].append(
                        {
                            "address": clean_address(resource["value"]),
                            "tags": resource["tags"],
                        }
                    )
            
            cleaned_data_dictionary["county_resources"].append(data_dict)
    
    with open(args.result_location, 'w') as fp:
        json.dump(cleaned_data_dictionary, fp, indent=4)
            
if __name__ == "__main__":
    clean_data()