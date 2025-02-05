import json
import csv

class MenuExtractor:
    def __init__(self, json_file, output_csv):
        self.json_file = json_file
        self.output_csv = output_csv
        self.data = self.load_json()

    def load_json(self):
        """Load JSON data from the file."""
        with open(self.json_file, "r", encoding="utf-8") as file:
            return json.load(file)
    
    def extract_menu_data(self):
        """Extract menu data from the JSON."""
        restaurant_keys = list(self.data["pages"]["restaurant"].keys())
        
        if len(restaurant_keys) != 1:
            raise ValueError("Expected exactly one restaurant ID, but found multiple or none.")
        
        restaurant_id = restaurant_keys[0]
        menus = self.data["pages"]["restaurant"][restaurant_id]["order"]["menuList"]["menus"]
        
        extracted_items = []
        
        for menu in menus:
            categories = menu["menu"].get("categories", [])
            
            for category in categories:
                items = category["category"].get("items", [])
                
                for item in items:
                    item_data = item["item"]
                    extracted_items.append([
                        item_data.get("name", "N/A"),
                        item_data.get("price", "N/A"),
                        item_data.get("desc", "N/A"),
                        item_data.get("item_image_url", "N/A"),
                        item_data.get("item_state", "N/A"),
                        item_data.get("rating", "N/A")
                    ])
        
        return extracted_items
    
    def save_to_csv(self, data):
        """Save extracted data to a CSV file."""
        headers = ["Name", "Price", "Description", "Image URL", "State", "Rating"]
        
        with open(self.output_csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)
    
    def run(self):
        """Execute the extraction and saving process."""
        extracted_data = self.extract_menu_data()
        self.save_to_csv(extracted_data)
        print(f"Data successfully extracted and saved to {self.output_csv}")

# Usage
if __name__ == "__main__":
    extractor = MenuExtractor("jsons/protein-chef.json", "output.csv")
    extractor.run()
