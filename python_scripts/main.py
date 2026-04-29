# Create a json file containing year, name, link, translators, publishers
# where the translators and publishers will be lists

from typing import Optional, List
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
import wikipedia
import requests
import json
from dotenv import load_dotenv, find_dotenv
from google import genai
import time

load_dotenv(find_dotenv())

@dataclass
class Translator:
    name: str
    link: Optional[str]

@dataclass
class Publisher:
    name: str
    link: Optional[str]

@dataclass
class ResponseSchema:
    translators: List[Translator]
    publishers: List[Publisher]


class Pipeline:
    RESPONSE_PATH = r"..\data\laureates_after_2000.json"
    DATA_PATH = r"..\data\laureates_after_2000.csv"

    def __init__(self, data_path: str = DATA_PATH, model_name: str = "gemma-4-31b-it"):
        # Note: "gemma-4" doesn't officially exist yet (latest is Gemma 2). 
        # Update model_name to exactly match the registry name of the model you are using.
        self.model_name = model_name
        self.client = genai.Client()
        
        path = Path(self.RESPONSE_PATH)
        
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.df = pd.read_csv(data_path)
            self.data = self.csv_to_dict(self.df) # Fixed method name and added self

    def csv_to_dict(self, df_csv: pd.DataFrame) -> List[dict]: # Added self
        return df_csv.to_dict(orient="records")

    def content_extractor(self, link: str): # Added self
        name = link.split("/")[-1]

        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "prop": "pageprops",
            "titles": name, # Fixed 'title' to 'name'
            "format": "json"
        }

        headers = {
            "User-Agent": "MyBot/1.0 (https://example.com/contact)" 
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        page_id = list(data["query"]["pages"].keys())[0]
        if page_id == '-1':
            raise ValueError(f"The link {link} has faulty strings in the name.")
        
        # 'wikipedia' is a module, not an object. Call it directly.
        content = wikipedia.page(pageid=page_id).content 
        
        return content

    def llm(self, content: str): # Removed the 'model' parameter to rely on self.model_name
        prompt = f"""You are an expert data extraction assistant. Your task is to carefully read a Wikipedia article about a Nobel Laureate in Literature and extract a list of Translators and Publishers who have directly worked with or published the author.

RULES:
1. ONLY extract people or companies explicitly mentioned as having translated or published the author's work.
2. If a Wikipedia link or URL is present in the text for that entity, include it in the "link" field. If there is no link, the value MUST be null.
3. If no translators or publishers are found, return an empty list [] for that category.
4. Output STRICTLY valid JSON. Do not include markdown formatting like ```json, and do not include any conversational text before or after the JSON.

EXPECTED JSON SCHEMA:
{{
  "translators": [
    {{"name": "string", "link": "string or null"}}
  ],
  "publishers": [
    {{"name": "string", "link": "string or null"}}
  ]
}}

EXAMPLE INPUT:
Gabriel García Márquez's masterpiece was famously translated into English by Gregory Rabassa. His primary English-language publisher was Harper & Row, while his works in Spanish were largely handled by Editorial Sudamericana (https://en.wikipedia.org/wiki/Editorial_Sudamericana).

EXAMPLE OUTPUT:
{{
  "translators": [
    {{"name": "Gregory Rabassa", "link": null}}
  ],
  "publishers": [
    {{"name": "Harper & Row", "link": null}},
    {{"name": "Editorial Sudamericana", "link": "https://en.wikipedia.org/wiki/Editorial_Sudamericana"}}
  ]
}}

Now, process the following article:

ARTICLE:
{content}

JSON OUTPUT:
"""
        # Fixed Indentation below!
        response = self.client.models.generate_content(
            model=self.model_name, 
            contents=prompt
        )
        
        return response.text 

    def process(self): # Added self
        # Loop over self.data directly. self.df might not exist if loaded from JSON
        for i, row in enumerate(self.data):
            link_new = row.get("link_new")
            if not link_new:
                continue

            print(f"Processing {link_new}...")

            def main():
                content = self.content_extractor(link_new)
                # row["content"] = content # Uncomment if you want to save the massive wikipedia article into the JSON
                
                response_text = self.llm(content)

                # response_text = """{
                #         "translators": [
                #             {"name": "string", "link": "string or null"}
                #         ],
                #         "publishers": [
                #             {"name": "string", "link": "string or null"}
                #         ]
                #     }"""
                
                # Robust JSON cleaning: In case the LLM uses markdown like ```json
                clean_text = response_text.strip().strip("`").removeprefix("json").strip()
                
                parsed_json = json.loads(clean_text)
                print(parsed_json)
                
                row["translators"] = parsed_json.get("translators", [])
                row["publishers"] = parsed_json.get("publishers", [])
                
                self.data[i] = row
            

            success = False
            while not success:
                try:
                    main()
                    success = True
                except Exception as e:
                    print(f"Error processing {link_new}: {e}")
                    print("Pause for 10s")
                    time.sleep(10)
                    print("Trying again now")             
                

        # Use self.RESPONSE_PATH since it's a class variable
        with open(self.RESPONSE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

        print("Processing complete!")


# To run this script:
if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.process()