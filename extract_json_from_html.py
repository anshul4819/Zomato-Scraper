import re
import os
import json

class HTMLToJSONProcessor:
    def __init__(self, directory=None):
        self.directory = directory or os.path.dirname(__file__)

    def process_all_html_files(self):
        """Process all `.html` files in the directory."""
        htmlPaths = os.path.join(self.directory, "htmls")
        for filename in os.listdir(htmlPaths):
            if filename.endswith(".html"):
                self.process_file(filename)

    def process_file(self, filename):
        """Process a single `.html` file and generate a `.json` file."""
        file_path = os.path.join(self.directory, "htmls", filename)
        
        with open(file_path, 'r', encoding="utf-8") as file:
            html_content = file.read()

        json_string = self.extract_json_string(html_content)
        if json_string is None:
            print(f"No JSON data found in {filename}. Skipping...")
            return

        json_data = self.parse_json(json_string, filename)
        if json_data is None:
            return

        self.save_json(json_data, filename.replace(".html", ".json"))

    def extract_json_string(self, html_content):
        """Extracts JSON string from `JSON.parse("...")` in the HTML content."""
        match = re.search(r'JSON\.parse\("(.+?)"\)', html_content, re.DOTALL)
        return match.group(1) if match else None

    def parse_json(self, json_string, filename):
        """Unescapes and loads the JSON string safely."""
        try:
            json_string = json_string.encode().decode('unicode_escape')  # Convert `\"` → `"`
            return json.loads(json_string)
        except json.decoder.JSONDecodeError as e:
            print(f"Error in {filename} at position {e.pos}: {e.msg}")
            start_pos = max(e.pos - 50, 0)
            end_pos = min(e.pos + 50, len(json_string))
            print(f"Context around the error:\n{json_string[start_pos:end_pos]}")
            return None

    def save_json(self, json_data, output_filename):
        """Saves formatted JSON data to a file."""
        output_file = os.path.join(self.directory, "jsons", output_filename)
        with open(output_file, 'w', encoding="utf-8") as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)
        print(f"Processed {output_filename}")

if __name__ == "__main__":
    processor = HTMLToJSONProcessor()
    processor.process_all_html_files()
