# Đọc nội dung từ file
with open("../../../../../../content_afterChange.txt", "r") as file:
    text = file.read()
import os
os.environ['CLASSPATH'] = "../../../../../target/minie-0.0.1-SNAPSHOT.jar"

# Uncomment to point to your java home (an example is given for arch linux)
# if you don't have it as an environment variable already.
# os.environ['JAVA_HOME'] = '/usr/lib/jvm/default'

# Import java classes in python with pyjnius' autoclass (might take some time)
from jnius import autoclass

CoreNLPUtils = autoclass('de.uni_mannheim.utils.coreNLP.CoreNLPUtils')
AnnotatedProposition = autoclass('de.uni_mannheim.minie.annotation.AnnotatedProposition')
MinIE = autoclass('de.uni_mannheim.minie.MinIE')
StanfordCoreNLP = autoclass('edu.stanford.nlp.pipeline.StanfordCoreNLP')
String = autoclass('java.lang.String')

# Dependency parsing pipeline initialization
parser = CoreNLPUtils.StanfordDepNNParser()
print("Text:", text)
# Input sentence
sentences = text.split(".")

triples_file_path = "../../../../../../triples.txt"

with open(triples_file_path, "w") as triples_file:
    # Lặp qua từng câu trong danh sách câu
    for sentence in sentences:
        # Tạo một đối tượng String từ câu
        sentence_obj = String(sentence.strip())

        try:
            # Generate the extractions (With SAFE mode (mode = 2))
            minie = MinIE(sentence_obj, parser, 2)

            # In ra kết quả cho câu hiện tại
            print("Input sentence:", sentence.strip())
            print("=============================")
            print("Extractions:")

            # Lặp qua các trích xuất và in ra
            for ap in minie.getPropositions().elements():
                if ap is not None: 
                    print("\tTriple:", ap.getTripleAsString())
                    print("\tFactuality:", ap.getFactualityAsString())
                    if ap.getAttribution().getAttributionPhrase() is not None:
                        print("\tAttribution:", ap.getAttribution().toStringCompact())
                    else:
                        print("\tAttribution: NONE")
                    print("\t----------")
                    
            for ap in minie.getPropositions().elements():
                if ap is not None: 
                    triples_file.write( ap.getTripleAsString() + "\n")

        except Exception as e:
            # In ra thông báo lỗi nếu có lỗi xảy ra trong quá trình xử lý câu
            print("An error occurred for sentence:", sentence.strip())
            print("Error:", e)

print("DONE!")