import os
from googletrans import Translator

def translate_text(text, source_lang='en', target_lang='vi'):
    translator = Translator()
    translated = translator.translate(text, src=source_lang, dest=target_lang)
    return translated.text

def main():
    # Check the original language from language_info.txt
    with open("language_info.txt", 'r', encoding='utf-8') as file:
        original_language = file.read().strip()

    if original_language == 'vi':
        print("Original content was in Vietnamese. Translating triples.txt to Vietnamese...")

        # Read triples.txt
        with open("triples.txt", 'r', encoding='utf-8') as file:
            triples_content = file.read()

        # Translate triples content
        translated_triples = translate_text(triples_content, source_lang='en', target_lang='vi')

        # Print translated triples
        print("Translated Triples:")
        print("===================")
        print(translated_triples)
        print("===================")

        # Write translated triples back to triples.txt
        with open("triples.txt", 'w', encoding='utf-8') as file:
            file.write(translated_triples)

        print("Translated triples saved to triples.txt")

if __name__ == "__main__":
    main()
