import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import logging

try:
    spacy.load("en_core_web_sm")
except OSError:
    logging.info("Downloading en_core_web_sm spacy model for Presidio...")
    from spacy.cli import download
    download("en_core_web_sm")

class PIIScrubbingService:
    def __init__(self):
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        # Initialize Presidio Analyzer and Anonymizer to use the SMALL model specifically
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        
        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, 
            supported_languages=["en"]
        )
        self.anonymizer = AnonymizerEngine()
        
    def scrub_and_vault(self, text: str) -> tuple[str, dict]:
        """
        Detects PII entities in the text, replaces them with deterministic tokens,
        and returns the sanitized text plus a mapping dictionary for re-hydration.
        """
        # We target specific entities
        entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "ORGANIZATION", "LOCATION"]
        
        # Analyze the text
        results = self.analyzer.analyze(text=text, entities=entities, language='en')
        
        # Sort results descending so replacements don't mess up indices
        results = sorted(results, key=lambda x: x.start, reverse=True)
        
        vault = {}
        sanitized_text = text
        counters = {ent: 1 for ent in entities}
        
        # To ensure we don't map "John" to <PERSON_1> in one place and <PERSON_2> in another,
        # we can keep track of seen text blocks, but Presidio works on exact spans.
        # For simplicity, we create a strict mapping of original exact sub-strings.
        substring_to_token = {}

        for result in results:
            original_str = text[result.start:result.end]
            
            if original_str not in substring_to_token:
                token = f"TOKEN_{result.entity_type}_{counters[result.entity_type]}"
                counters[result.entity_type] += 1
                substring_to_token[original_str] = token
                vault[token] = original_str
            else:
                token = substring_to_token[original_str]
                
            # Replace in text
            sanitized_text = sanitized_text[:result.start] + f"<{token}>" + sanitized_text[result.end:]
            
        return sanitized_text, vault

    def rehydrate(self, obj, vault: dict):
        """
        Recursively walks through a parsed JSON object (dict, list, str) and
        replaces any tokens back to their original strings.
        """
        if isinstance(obj, str):
            res = obj
            for token, original_str in vault.items():
                target = f"<{token}>"
                if target in res:
                    res = res.replace(target, original_str)
            return res
        elif isinstance(obj, list):
            return [self.rehydrate(item, vault) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.rehydrate(v, vault) for k, v in obj.items()}
        else:
            return obj

# Singleton instance
pii_scrubber = PIIScrubbingService()
