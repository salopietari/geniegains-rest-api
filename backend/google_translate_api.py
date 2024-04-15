import os
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
load_dotenv()

service_account_path = os.getenv("GOOGLE_CLOUD_TRANSLATION_SERVICE_ACCOUNT_PATH")

def authenticate():
    translate_client = translate.Client.from_service_account_json(service_account_path)
    return translate_client

def detect_language(text):
    client = authenticate()
    result = client.detect_language(text)
    return result['language']

def translate_text(text, target_language):
    client = authenticate()
    result = client.translate(text, target_language)
    return result['translatedText']
