"""
Your Categorized Health Resource Crawler
Fill in the TODO sections to build your own crawler!
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
from datetime import datetime

class MyCategorizedCrawler:
    def __init__(self):
        # TODO: Set up a requests session with appropriate headers
        # Hint: Use requests.Session() and set User-Agent header
        self.session = requests.Session()  # Replace with your session setup
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15"
        })
        
        # Create output directory if it doesn't exist
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Health topic keywords for auto-tagging
        self.health_keywords = {
            'flu': [r'flu', r'influenza', r'flu shot'],
            'covid19': [r'covid', r'covid-19', r'coronavirus'],
            'vaccination': [r'vaccine', r'vaccination', r'immunization'],
            'pediatric': [r'pediatric', r'children', r'kids', r'child'],
            'dental': [r'dental', r'dentist', r'teeth'],
            'mental_health': [r'mental health', r'counseling'],
            'emergency': [r'emergency', r' er(.| )', r'24 hour'],
            # TODO: Add more keywords as you find them!
        }
    
    def get_page(self, url):
        """
        TODO: Fetch a web page and return BeautifulSoup object
        
        Steps:
        1. Use self.session.get(url) to fetch the page
        2. Check if the request was successful (response.raise_for_status())
        3. Parse with BeautifulSoup(response.content, 'html.parser')
        4. Return the soup object
        5. Handle exceptions and return None if there's an error
        """
        try:
            print(f"Fetching: {url}")
            # TODO: Implement page fetching logic
            response = self.session.get(url)  # Replace with actual request
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')      # Replace with actual parsing
            return soup
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def auto_tag_resource(self, text: str, context=""):
        """
        TODO: Automatically assign tags based on keywords
        
        Look through self.health_keywords and see which ones match
        the text or context you found.
        """
        found_tags = []
        
        # Combine text and context for better matching
        full_text = (text + " " + context).lower()
        
        # TODO: Loop through health_keywords and check for matches
        for tag, keywords in self.health_keywords.items():
            # TODO: Check if any keyword appears in full_text
            # Hint: Use 'any(keyword in full_text for keyword in keywords)'
            if any(keyword in re.findall(keyword, full_text) for keyword in keywords):
                found_tags.append(tag)
        return found_tags
    
    def find_phone_numbers(self, text, context=""):
        """
        TODO: Find phone numbers in text using regex patterns
        
        Common patterns:
        - 555-123-4567
        - (555) 123-4567
        - 555.123.4567
        """
        phone_numbers = []
                
        # TODO: Create regex patterns for phone numbers
        patterns = [
            # Add your patterns here
            r'[0-9]{3}-[0-9]{3}-[0-9]{4}',
            r'\([0-9]{3}\) [0-9]{3}-[0-9]{4}',
            r'[0-9]{3}\.[0-9]{3}\.[0-9]{4}',
        ]
        
        # TODO: Use re.findall to find matches for each pattern
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phone_numbers.extend(matches)
        # Remove duplicates
        unique_phones = list(set(phone_numbers))
        
        # Convert to categorized format
        results = []
        for phone in unique_phones:
            tags = self.auto_tag_resource(phone, context)
            
            # TODO: Add special handling for crisis/emergency numbers
            if 'crisis' in context.lower() or 'suicide' in context.lower():
                tags.append('crisis_hotline')
            
            results.append({
                'category': 'CONTACT_INFO',
                'type': 'phone_number',
                'value': phone,
                'tags': tags,
                'context': context
            })
        
        return results
    
    def find_addresses(self, soup: BeautifulSoup, context=""):
        """
        TODO: Look for addresses in the HTML
        
        Hint: Look for:
        - Elements with class names like 'address', 'location'
        - HTML <address> tags
        - Text that contains street names and numbers
        """
        results = []
                        
        # TODO: Use soup.select() to find elements that might contain addresses
        address_selectors = [
            '.address',
            '.location', 
            '.contact-info',
            'address',  # HTML address tag
            '.fb__facility-address',
            # TODO: Add more selectors you discover
        ]
        
        for selector in address_selectors:
            # TODO: Find elements matching the selector
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                                
                # TODO: Check if text looks like an address
                if self.looks_like_address(text):
                    tags = self.auto_tag_resource(text, context)
                    
                    results.append({
                        'category': 'LOCATION',
                        'type': 'address',
                        'value': text,
                        'tags': tags,
                        'context': context
                    })
        
        return results
    
    def find_facilities(self, soup, context=""):
        """
        TODO: Look for healthcare facility names
        
        Hint: Look in headings (h1, h2, h3) and elements with 
        'clinic', 'facility', 'hospital' in class names
        """
        results = []
        
        # TODO: Look for facility names in different places
        facility_selectors = [
            'h1', 'h2', 'h3',  # Headings often contain facility names
            '.facility-name',
            '.clinic-name',
            # TODO: Add more selectors
        ]
        
        for selector in facility_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                
                # TODO: Check if text looks like a facility name
                if self.looks_like_facility_name(text):
                    tags = self.auto_tag_resource(text, context)
                    
                    # TODO: Add facility-specific tags
                    facility_lower = text.lower()
                    if 'hospital' in facility_lower:
                        tags.append('hospital')
                    elif 'clinic' in facility_lower:
                        tags.append('clinic')
                    # TODO: Add more facility types
                    
                    results.append({
                        'category': 'FACILITY',
                        'type': 'facility_name',
                        'value': text,
                        'tags': tags,
                        'context': context
                    })
        
        return results
    
    def looks_like_address(self, text):
        """
        TODO: Check if text looks like an address
        
        Hints:
        - Should contain numbers
        - Should contain street words (street, avenue, road, etc.)
        - Should be reasonable length
        """
        # TODO: Implement address validation logic
        street_words = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 
                       'boulevard', 'blvd', 'drive', 'dr', 'lane', 'ln']
        
        text_lower = text.lower()
        has_number = any(char.isdigit() for char in text)
        has_street_word = any(word in text_lower for word in street_words)
        is_reasonable_length = 10 < len(text) < 200
        
        return has_number and has_street_word and is_reasonable_length
    
    def looks_like_facility_name(self, text):
        """
        TODO: Check if text looks like a healthcare facility name
        
        Hints:
        - Should contain health-related keywords
        - Should be reasonable length
        - Should not be too generic
        """
        health_keywords = ['clinic', 'hospital', 'medical', 'health', 'center', 
                          'pharmacy', 'dental', 'care', 'urgent', 'family']
        
        text_lower = text.lower()
        has_health_keyword = any(keyword in text_lower for keyword in health_keywords)
        is_reasonable_length = 5 < len(text) < 100
        
        return has_health_keyword and is_reasonable_length
    
    def crawl_page(self, url):
        """
        TODO: Put it all together!
        
        1. Get the page using self.get_page()
        2. Extract phone numbers, addresses, and facilities
        3. Return a dictionary with your results
        """
        soup = self.get_page(url)
        if not soup:
            return {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'resources': [],
                'error': 'Failed to fetch page'
            }
        
        # TODO: Extract all resource types
        all_resources = []
        
        # Get page text for phone number extraction
        page_text = soup.get_text()
        
        # TODO: Extract phone numbers from page text
        phone_results = self.find_phone_numbers(page_text, "general page content")
        all_resources.extend(phone_results)
        
        # TODO: Extract addresses from HTML structure
        address_results = self.find_addresses(soup, "page structure")
        all_resources.extend(address_results)
        
        # TODO: Extract facility names
        facility_results = self.find_facilities(soup, "page headings")
        all_resources.extend(facility_results)
        
        return {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'resources': all_resources
        }
    
    def save_results(self, results, filename=None):
        """
        Save categorized results with summary statistics
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"my_results_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # TODO: Add summary statistics
        summary = {
            'total_resources': len(results.get('resources', [])),
            'by_category': {},
            'by_tag': {},
            'crawl_info': {
                'url': results.get('url'),
                'timestamp': results.get('timestamp'),
                'student_name': 'Joshua Yamada'
            }
        }
        
        # TODO: Count resources by category and tag
        for resource in results.get('resources', []):
            category = resource.get('category', 'Unknown')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            for tag in resource.get('tags', []):
                summary['by_tag'][tag] = summary['by_tag'].get(tag, 0) + 1
        
        # Save complete results
        output = {
            'summary': summary,
            'detailed_results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {filepath}")
        return filepath
    
    def print_results(self, results):
        """
        Pretty print the results
        """
        print(f"\n--- Results for {results['url']} ---")
        print(f"Timestamp: {results['timestamp']}")
        
        resources = results.get('resources', [])
        if not resources:
            print("No resources found.")
            return
        
        # Group by category
        by_category = {}
        for resource in resources:
            category = resource['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(resource)
        
        for category, items in by_category.items():
            print(f"\n📋 {category} ({len(items)} items):")
            for item in items:
                tags_str = ", ".join(item['tags']) if item['tags'] else "general"
                print(f"  • {item['value']}")
                print(f"    Tags: {tags_str}")

# Test your crawler here!
if __name__ == "__main__":
    crawler = MyCategorizedCrawler()
    
    # TODO: Choose a website to test (start with a simple one!)
    # test_url = "https://www.cdc.gov/flu/treatment/index.html"
    test_url = "http://www.co.merced.ca.us/index.aspx?nid=82"
    
    print("Testing your crawler...")
    print("Make sure to complete the TODO sections first!")
    
    # TODO: Crawl the page and print results
    results = crawler.crawl_page(test_url)
    crawler.print_results(results)
    
    # TODO: Save results
    crawler.save_results(results, "test_single_site.json")
    
    print("\n📁 Check the 'output' folder for your results!")
    print("Once this works, try with a local health department website.")