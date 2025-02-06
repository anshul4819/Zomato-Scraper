import os
import requests

def get_website_html():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        restaurant_name_file_path = os.path.join(base_dir, "restaurant_names.txt")
        
        if not os.path.exists(restaurant_name_file_path):
            print(f"Error: {restaurant_name_file_path} not found.")
            return

        with open(restaurant_name_file_path, "r", encoding="utf-8") as file:
            restaurant_names = file.read().splitlines()

        for name in restaurant_names:
            restaurant_url = base_url.replace("{restaurant-name}", name)
            response = requests.get(restaurant_url, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                file_path = os.path.join(html_dir, f"{name}.html")

                with open(file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)
                print(f"Saved HTML for {name} to {file_path}")
            else:
                print(f"Failed to retrieve HTML for {name} (status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the website: {e}")

if __name__ == "__main__":
    base_url = "https://www.zomato.com/bangalore/{restaurant-name}/order"
    base_dir = os.getcwd()
    html_dir = os.path.join(base_dir, "htmls")
    os.makedirs(html_dir, exist_ok=True)
    
    get_website_html()
