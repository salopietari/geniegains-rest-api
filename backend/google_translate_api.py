from google.cloud import translate_v2 as translate

def authenticate():
    translate_client = translate.Client.from_service_account_json('C:\\Users\\pieta\\OneDrive\\Tiedostot\\GitHub\\GenieGains-restapi\\geniegains_google_cloud_translation_service_account_details.json')
    return translate_client

def detect_language(text):
    client = authenticate()
    result = client.detect_language(text)
    return result['language']

def translate_text(text, target_language):
    client = authenticate()
    result = client.translate(text, target_language=target_language)
    return result['translatedText']
