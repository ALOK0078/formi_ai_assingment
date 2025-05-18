import pandas as pd
from fuzzywuzzy import process

class KnowledgeBase:
    def __init__(self):
        self.properties = self._load_properties()
        self.faqs = self._load_faqs()

    def _load_properties(self):
        """Load properties from CSV with error handling"""
        try:
            return pd.read_csv('data/properties.csv')
        except FileNotFoundError:
            raise Exception("properties.csv not found in data directory")
        except pd.errors.ParserError:
            raise Exception("Error parsing properties.csv")

    def _load_faqs(self):
        """Load FAQs from CSV (future use)"""
        try:
            return pd.read_csv('data/faqs.csv')
        except FileNotFoundError:
            return pd.DataFrame()

    def is_valid_city(self, city_input: str) -> bool:
       
        city_input = city_input.strip().lower()
        return any(city_input == str(city).strip().lower() for city in self.properties['city'].unique())

    def get_properties(self, city_input: str):
        
        city_input = city_input.strip().lower()
        return list(
            self.properties[self.properties['city'].str.lower() == city_input]['primary_name']
        )

    def get_property(self, city_input: str, property_input: str):
        
        city_input = city_input.strip().lower()
        property_input = property_input.strip().lower()
        df = self.properties[self.properties['city'].str.lower() == city_input]
        for _, row in df.iterrows():
            if (property_input == str(row['primary_name']).strip().lower() or
                property_input == str(row['address']).strip().lower()):
                # Return as dict for context update
                return {
                    'property_name': row['primary_name'],
                    'address': row['address'],
                    'city': row['city']
                }
        # Optionally, fuzzy match for user typos
        if not df.empty:
            choices = list(df['primary_name']) + list(df['address'])
            match, score = process.extractOne(property_input, choices)
            if score > 85:  # Threshold for fuzzy match
                row = df[(df['primary_name'] == match) | (df['address'] == match)].iloc[0]
                return {
                    'property_name': row['primary_name'],
                    'address': row['address'],
                    'city': row['city']
                }
        return None

    def answer_faq(self, question: str, city: str = None) -> str:
        """(Optional) Return best-matching FAQ answer, optionally filtered by city."""
        if self.faqs.empty:
            return "Sorry, I couldn't find an answer to your question."
        faqs = self.faqs
        if city:
            faqs = faqs[faqs['city'].str.lower() == city.strip().lower()]
        questions = faqs['question'].tolist()
        if not questions:
            return "Sorry, I couldn't find an answer to your question."
        match, score, idx = process.extractOne(question, questions, scorer=process.fuzz.token_sort_ratio, score_cutoff=70)
        if score and score > 70:
            return faqs.iloc[idx]['answer']
        return "Sorry, I couldn't find an answer to your question."
