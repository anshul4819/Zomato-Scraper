from PIL import Image
import requests
import io
import base64
from typing import Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import json
import os
import genai

class NutritionAnalysisService:
    def __init__(self):
        self.openai_client = OpenAI(api_key="")
        self.anthropic_client = Anthropic(api_key="")
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

    def compress_image(self, image_url: str, max_size: tuple = (800, 800)) -> bytes:
        """
        Download and compress image to specified max dimensions
        """
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        compressed_buffer = io.BytesIO()
        image.save(compressed_buffer, format='JPEG', quality=85)
        return compressed_buffer.getvalue()

    def analyze_image_with_claude(self, compressed_image: bytes, dish_description: str) -> Dict[str, Any]:
        """
        Analyze image nutrition using Claude
        """
        try:
            response = self.anthropic_client.messages.create(
                model="Claude 3.5 Sonnet 2024-10-22",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"""Analyze the nutritional content of this dish: {dish_description}

Please return ONLY a JSON object with the following structure:
{{
    "calories": number,
    "macronutrients": {{
        "protein": number,
        "carbohydrates": number,
        "fat": number
    }},
    "micronutrients": {{
        "vitamins": [string],
        "minerals": [string]
    }}
}}
"""},
                            {"type": "image", "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64.b64encode(compressed_image).decode('utf-8')
                            }}
                        ]
                    }
                ]
            )
            return json.loads(response.content[0].text)
        except Exception as e:
            print(f"Claude analysis error: {e}")
            return {}

    def analyze_image_with_gpt(self, compressed_image: bytes, dish_description: str) -> Dict[str, Any]:
        """
        Analyze image nutrition using GPT
        """
        try:
            response = self.openai_client.chat.completions.create(
                model= "gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            f"""Analyze the nutritional content of this dish: {dish_description}

    Please return ONLY a JSON object with the following structure:
    {{
        "calories": number,
        "macronutrients": {{
            "protein": number,
            "carbohydrates": number,
            "fat": number
        }},
        "micronutrients": {{
            "vitamins": [string],
            "minerals": [string]
        }}
    }}
    """,
                            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(compressed_image).decode('utf-8')}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"GPT analysis error: {e}")
            return {}

    def analyze_image_with_gemini(self, compressed_image: bytes, dish_description: str) -> Dict[str, Any]:
        """
        Analyze image nutrition using Google Gemini
        """
        try:
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([
                f"""Analyze the nutritional content of this dish: {dish_description}

Please return ONLY a JSON object with the following structure:
{{
    "calories": number,
    "macronutrients": {{
        "protein": number,
        "carbohydrates": number,
        "fat": number
    }},
    "micronutrients": {{
        "vitamins": [string],
        "minerals": [string]
    }}
}}
""", 
                Image.open(io.BytesIO(compressed_image))
            ])
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return {}

    def analyze_dish(self, dish_description: str, image_url: str) -> Dict[str, Any]:
        """
        Main method to analyze dish nutrition across multiple models
        """
        compressed_image = self.compress_image(image_url)

        claude_result = self.analyze_image_with_claude(compressed_image, dish_description)
        gpt_result = self.analyze_image_with_gpt(compressed_image, dish_description)
        # gemini_result = self.analyze_image_with_gemini(compressed_image, dish_description)

        aggregated_result = {
            "calories": (claude_result.get("calories", 0) + 
                         gpt_result.get("calories", 0)) / 2,
            "macronutrients": {
                "protein": (claude_result.get("macronutrients", {}).get("protein", 0) + 
                            gpt_result.get("macronutrients", {}).get("protein", 0)) / 2,
                "carbohydrates": (claude_result.get("macronutrients", {}).get("carbohydrates", 0) + 
                                  gpt_result.get("macronutrients", {}).get("carbohydrates", 0)) / 2,
                "fat": (claude_result.get("macronutrients", {}).get("fat", 0) + 
                        gpt_result.get("macronutrients", {}).get("fat", 0)) / 2
            },
            "micronutrients": {
                "vitamins": list(set(
                    claude_result.get("micronutrients", {}).get("vitamins", []) +
                    gpt_result.get("micronutrients", {}).get("vitamins", [])
                )),
                "minerals": list(set(
                    claude_result.get("micronutrients", {}).get("minerals", []) +
                    gpt_result.get("micronutrients", {}).get("minerals", [])
                ))
            }
        }

        return aggregated_result

if __name__ == "__main__":
    service = NutritionAnalysisService()
    result = service.analyze_dish(
        "Protein - 57g Health ka tasty dose coming your way- try our Chicken Keema & High Protein Roti Meal! Enjoy the lip-smacking fusion of chicken keema and protein-packed roti (3 pc), providing you with a satisfyingly delicious meal. May contain Soy, Gluten, Groundnuts, and Other Nuts.Served Along with 40g High Protein Mixture", 
        "https://b.zmtcdn.com/data/dish_photos/a54/dfa4e1770ac1bdb746ccd752c0379a54.jpg"
    )
    print(result)