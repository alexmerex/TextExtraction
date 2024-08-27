import tkinter as tk
from tkinter import filedialog
import os
from googletrans import Translator

def is_vietnamese(text):
    # Function to check if text is Vietnamese (naive approach)
    vietnamese_characters = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
    return any(char in vietnamese_characters for char in text)

def translate_text(text, source_lang='vi', target_lang='en'):
    translator = Translator()
    translated = translator.translate(text, src=source_lang, dest=target_lang)
    return translated.text

def main():
    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Show a file dialog to select the content file
    file_path = filedialog.askopenfilename(title="Select the content file", filetypes=[("Text files", "*.txt")])

    if not file_path:
        print("No file selected. Exiting.")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    is_vietnamese_content = is_vietnamese(content)
    if is_vietnamese_content:
        print("Vietnamese content detected. Translating to English...")
        translated_content = translate_text(content)
        content = translated_content

    # Save the content to content.txt
    with open("content.txt", 'w', encoding='utf-8') as file:
        file.write(content)

    # Save the language information
    with open("language_info.txt", 'w', encoding='utf-8') as file:
        file.write('vi' if is_vietnamese_content else 'en')

    print("Content prepared and saved as content.txt")

if __name__ == "__main__":
    main()
