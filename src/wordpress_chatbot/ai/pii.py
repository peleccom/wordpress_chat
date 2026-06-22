from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.predefined_recognizers import EmailRecognizer, SpacyRecognizer
from presidio_anonymizer import AnonymizerEngine

nlp_engine = SpacyNlpEngine(models=[{"lang_code": "en", "model_name": "en_core_web_md"}])
registry = RecognizerRegistry(
    recognizers=[
        EmailRecognizer(),
        SpacyRecognizer(supported_entities=["PERSON"]),
    ]
)

analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
anonymizer = AnonymizerEngine()
