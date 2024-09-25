# README.txt

## Overview
This script reads text data from a file, processes it using Java-based Natural Language Processing (NLP) tools integrated into Python, and extracts relational triples from the input sentences. The extracted triples are then saved to a separate file. The script utilizes the Stanford CoreNLP library for dependency parsing and MinIE for information extraction.

## Prerequisites
1. **Java Development Kit (JDK)**: Ensure that the JDK is installed and properly set up in your system environment.
2. **Pyjnius**: A Python library for accessing Java classes.
3. **Stanford CoreNLP**: This library is required for parsing text.
4. **MinIE**: The information extraction tool used in this script.
5. **Classpath Configuration**: The `CLASSPATH` environment variable should point to the location of the MinIE JAR file.

## Setup

### 1. Install Pyjnius
You can install Pyjnius using pip:
```bash
pip install pyjnius
```

### 2. Java Environment Setup
Make sure your `JAVA_HOME` environment variable is set correctly. If it’s not set, uncomment the following line in the script and adjust the path according to your system:
```python
# os.environ['JAVA_HOME'] = '/path/to/your/java/home'
```

### 3. Set CLASSPATH
The `CLASSPATH` environment variable should be set to the location of the `minie-0.0.1-SNAPSHOT.jar` file. This is already configured in the script as:
```python
os.environ['CLASSPATH'] = "../../../../../target/minie-0.0.1-SNAPSHOT.jar"
```
Ensure the path is correct relative to your script's location.

### 4. Input File
The input text file should be located at `../../../../../../content_afterChange.txt` relative to the script. Ensure the file exists and contains the sentences you want to process.

## Usage
1. **Run the Script**: Execute the script using Python:
    ```bash
    python script_name.py
    ```
   The script will read sentences from `content_afterChange.txt`, process each sentence to extract triples, and save the results in `triples.txt`.

2. **Output File**: The extracted triples are saved to `../../../../../../triples.txt`. Each line in this file corresponds to a relational triple extracted from the input sentences.

## Error Handling
The script includes basic error handling. If an error occurs while processing a sentence, the error message will be printed to the console along with the problematic sentence. The script will then continue processing the next sentence.

## Customization
- **SAFE Mode**: The extraction is performed in SAFE mode (`mode = 2`). You can adjust the mode according to your needs.
- **File Paths**: Update the file paths for both input and output files if necessary.
- **Java Classes**: If you want to use other Java classes or customize the extraction process, modify the relevant parts of the script.

## Troubleshooting
- **Classpath Issues**: Ensure the `CLASSPATH` is correctly set to include all necessary JAR files.
- **Java Environment**: Verify that the `JAVA_HOME` environment variable is set and points to the correct JDK path.

## Additional Information
For more information on MinIE and Stanford CoreNLP, refer to their respective documentation:

- [Stanford CoreNLP Documentation](https://stanfordnlp.github.io/CoreNLP/)
- [MinIE GitHub Repository](https://github.com/your-minie-repository)

## License
Include license information if applicable.

## Acknowledgments
This script uses various open-source libraries. Thanks to their developers for making them available.

---
