
# Data Folder

This folder contains data files used for crawling and analysis.

## websites/

Contains CSV files for each US state, listing public health organizations and related metadata. Each file is named `us-XX.csv` where `XX` is the two-letter state code (e.g., `us-ca.csv` for California, `us-tx.csv` for Texas).

Websites are accessed 1 by 1, with 2 seconds between each site

### CSV Format

The CSV files use semicolon (`;`) as the delimiter. The main columns are:

- `name`: Name of the PHapp community (e.g., county, borough, or health department)
- `parent_id`: Parent community (state or group)
- `community_id`: Community identifier
- `category`: Type of community (e.g., County, Borough, Town, Group)
- `pha`: Whether community has a public health authority (TRUE/FALSE)
- `population_proper`: Population served by the organization
- `state_id`: Two-letter state code (e.g., CA, TX, NY)
- `pha_url`: Website URL for the health department or organization

Other columns may be present for additional metadata.

### Example row

```
name;parent_id;community_id;category;pha;population_proper;state_id;pha_url
Benton County;us-ar-nw;us-ar-benton;County;TRUE;279141;AR;
```

Each row represents a public health organization in the state, with its website and relevant details.

### Usage in Your Crawler
```python
import csv

# Load a state's public health organizations
with open('data/websites/us-ca.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        print(f"Crawling {row['name']}: {row['pha_url']}")
```

## Notes
- Some websites may be offline or have changed URLs
- Always test with a small sample first
- Respect rate limits when crawling multiple sites