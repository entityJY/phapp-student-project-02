"""
Your Batch Health Resource Crawler
Learn to process multiple websites from CSV files!
"""

import csv
import time
import json
import os
from datetime import datetime
from my_crawler import MyCategorizedCrawler
from pathlib import Path

class MyBatchCrawler:
    def __init__(self):
        self.crawler = MyCategorizedCrawler()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_state_websites(self, state_code):
        """
        TODO: Load health department websites from CSV file
        
        The CSV file will be at: f"../data/state_websites/us-{state_code}.csv"
        
        CSV columns:
        - county: County name
        - department_name: Full name of health department  
        - website_url: URL to crawl
        - population: County population (optional)
        """
        websites = []
        
        # TODO: Open and read the CSV file
        # Hint: Use csv.DictReader
        filename = f"{str(Path(__file__).absolute())[:-20]}/../data/websites/us-{state_code.lower()}.csv"
        
        try:
            # TODO: Read each row and add to websites list
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    websites.append({
                        'county': row['name'],
                        'department_name': row['community_id'],
                        'website_url': row['pha_url'],
                        'population': row.get('population', 'Unknown')
                    })
            
            print(f"Loaded {len(websites)} health departments for {state_code.upper()}")
            
        except FileNotFoundError:
            print(f"File not found: {filename}")
            print("Make sure you're running from the student_template/ directory")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        
        return websites
    
    def crawl_multiple_sites(self, websites, max_sites=3):
        """
        TODO: Crawl multiple websites from your list
        
        Important: 
        - Add time.sleep() between requests to be polite!
        - Handle errors gracefully (some sites might be down)
        - Keep track of your results
        """
        results = []
        
        # TODO: Loop through websites (limit to max_sites for testing)
        for i, site in enumerate(websites[:max_sites]):
            print(f"\n[{i+1}/{min(len(websites), max_sites)}] Crawling {site['county']} County")
            print(f"Department: {site['department_name']}")
            print(f"URL: {site['website_url']}")
            
            try:
                # TODO: Crawl the site using your crawler
                site_results = self.crawler.crawl_page(site['website_url'])
                
                # TODO: Add metadata from the CSV
                site_results.update({
                    'county': site['county'],
                    'department_name': site['department_name'],
                    'population': site['population']
                })
                
                # TODO: Add the results to your list
                results.append(site_results)
                
                # Show quick summary
                num_resources = len(site_results.get('resources', []))
                print(f"✅ Found {num_resources} resources")
                
            except Exception as e:
                print(f"❌ Error crawling {site['county']}: {e}")
                # TODO: Add error result so we don't lose track
                results.append({
                    'county': site['county'],
                    'department_name': site['department_name'],
                    'url': site['website_url'],
                    'error': str(e),
                    'resources': []
                })
            
            # TODO: Wait between requests (time.sleep)
            # Be polite - don't hammer the servers!
            if i < min(len(websites), max_sites) - 1:
                print("Waiting 2 seconds...")
                time.sleep(2)
        
        return results
    
    def save_batch_results(self, results, state_code):
        """
        Save batch crawling results with proper naming
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        json_filename = f"batch_{state_code}_{timestamp}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        
        batch_data = {
            "crawl_info": {
                "state": state_code.upper(),
                "timestamp": datetime.now().isoformat(),
                "total_sites": len(results),
                "successful_crawls": len([r for r in results if 'error' not in r]),
                "student_name": "Joshua Yamada"  # TODO: Put your name!
            },
            "results": results
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Detailed results: {json_path}")
        
        # Create summary CSV
        self.create_summary_csv(results, state_code, timestamp)
        
        # Create text report
        self.create_text_report(results, state_code, timestamp)
    
    def create_summary_csv(self, results, state_code, timestamp):
        """
        TODO: Create a CSV summary of your batch crawling results
        """
        csv_filename = f"batch_{state_code}_summary_{timestamp}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        
        # TODO: Write CSV with summary statistics for each county
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # TODO: Write header row
            writer.writerow(['County', 'Department', 'URL', 'Phones Found', 
                           'Addresses Found', 'Facilities Found', 'Total Resources', 'Status'])
            
            # TODO: Write data rows
            for result in results:
                if 'error' in result:
                    # Handle error cases
                    writer.writerow([
                        result.get('county', 'Unknown'),
                        result.get('department_name', 'Unknown'),
                        result.get('url', ''),
                        0, 0, 0, 0, 'ERROR'
                    ])
                else:
                    # Count resources by type
                    resources = result.get('resources', [])
                    phone_count = len([r for r in resources if r.get('type') == 'phone_number'])
                    address_count = len([r for r in resources if r.get('type') == 'address'])
                    facility_count = len([r for r in resources if r.get('type') == 'facility_name'])
                    total_count = len(resources)
                    
                    writer.writerow([
                        result.get('county', 'Unknown'),
                        result.get('department_name', 'Unknown'),
                        result.get('url', ''),
                        phone_count,
                        address_count,
                        facility_count,
                        total_count,
                        'SUCCESS'
                    ])
        
        print(f"✅ Summary CSV: {csv_path}")
    
    def create_text_report(self, results, state_code, timestamp):
        """
        Create a human-readable report of batch crawling
        """
        report_filename = f"batch_{state_code}_report_{timestamp}.txt"
        report_path = os.path.join(self.output_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"BATCH CRAWLING REPORT - {state_code.upper()}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Crawled: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Sites: {len(results)}\n")
            
            # Count successful vs failed crawls
            successful = [r for r in results if 'error' not in r]
            failed = [r for r in results if 'error' in r]
            
            f.write(f"Successful: {len(successful)}\n")
            f.write(f"Failed: {len(failed)}\n\n")
            
            # Summary statistics
            total_resources = sum(len(r.get('resources', [])) for r in successful)
            
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Resources Found: {total_resources}\n")
            
            # Count by category
            category_counts = {}
            for result in successful:
                for resource in result.get('resources', []):
                    category = resource.get('category', 'Unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            for category, count in category_counts.items():
                f.write(f"{category}: {count}\n")
            
            f.write("\n")
            
            # Top performers
            f.write("TOP COUNTIES BY RESOURCES FOUND\n")
            f.write("-" * 35 + "\n")
            
            county_totals = []
            for result in successful:
                total = len(result.get('resources', []))
                county_totals.append((result.get('county', 'Unknown'), total))
            
            county_totals.sort(key=lambda x: x[1], reverse=True)
            
            for county, total in county_totals:
                f.write(f"{county}: {total} resources\n")
            
            if failed:
                f.write(f"\nFAILED CRAWLS\n")
                f.write("-" * 15 + "\n")
                for result in failed:
                    f.write(f"{result.get('county', 'Unknown')}: {result.get('error', 'Unknown error')}\n")
            
            f.write(f"\nDetailed results available in JSON format.\n")
        
        print(f"✅ Text report: {report_path}")
    
    def print_batch_summary(self, results):
        """
        Print a summary of batch crawling results to console
        """
        print(f"\n=== BATCH CRAWLING SUMMARY ===")
        print(f"Total sites processed: {len(results)}")
        
        successful = [r for r in results if 'error' not in r]
        failed = [r for r in results if 'error' in r]
        
        print(f"Successful crawls: {len(successful)}")
        print(f"Failed crawls: {len(failed)}")
        
        if successful:
            total_resources = sum(len(r.get('resources', [])) for r in successful)
            print(f"Total resources found: {total_resources}")
            
            # Show top counties
            county_totals = [(r.get('county'), len(r.get('resources', []))) for r in successful]
            county_totals.sort(key=lambda x: x[1], reverse=True)
            
            print(f"\nTop counties by resources:")
            for county, count in county_totals[:3]:
                print(f"  {county}: {count} resources")

# Test your batch crawler!
if __name__ == "__main__":
    print("Testing your batch crawler...")
    print("Make sure you completed my_crawler.py first!")
    
    batch_crawler = MyBatchCrawler()
    
    # TODO: Choose a state to test with
    state = "ca"  # or "or", "tx", etc.
    
    # TODO: Load the websites
    print(f"\nLoading websites for {state.upper()}...")
    websites = batch_crawler.load_state_websites(state)
    
    if websites:
        print(f"Found {len(websites)} health departments")
        
        # TODO: Crawl a few sites (start small!)
        print(f"\nCrawling first 15 sites...")
        results = batch_crawler.crawl_multiple_sites(websites, max_sites=15)
        
        # TODO: Show summary
        batch_crawler.print_batch_summary(results)
        
        # TODO: Save your results
        batch_crawler.save_batch_results(results, state)
        
        print("\n📁 Check the 'output' folder for all your results!")
    else:
        print("No websites loaded. Check the file path and try again.")
    
    print("\nDone! Try increasing max_sites once this works.")