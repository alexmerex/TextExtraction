package edu.ncsu.artificialGuy;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import edu.stanford.nlp.coref.CorefCoreAnnotations.CorefChainAnnotation;
import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.coref.data.CorefChain.CorefMention;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentenceIndexAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

public final class NLP {
    private final StanfordCoreNLP pipeline;

    private NLP() {
        Properties properties = new Properties();
        properties.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,parse,coref");
        properties.setProperty("coref.algorithm", "neural");
        pipeline = new StanfordCoreNLP(properties);
    }

    public static NLP getInstance() {
        return Holder.INSTANCE;
    }

    public String resolveCoRef(String text) {
        Annotation document = new Annotation(text);
        pipeline.annotate(document);

        Map<Integer, CorefChain> corefs = document.get(CorefChainAnnotation.class);
        List<CoreMap> sentences = document.get(SentencesAnnotation.class);
        Map<Integer, Map<Integer, Replacement>> replacements = buildReplacements(corefs, sentences);
        StringBuilder resolved = new StringBuilder();

        for (CoreMap sentence : sentences) {
            List<CoreLabel> tokens = sentence.get(TokensAnnotation.class);
            int sentenceNumber = sentence.get(SentenceIndexAnnotation.class) + 1;
            Map<Integer, Replacement> sentenceReplacements = replacements.get(sentenceNumber);

            for (int tokenPosition = 1; tokenPosition <= tokens.size();) {
                Replacement replacement = sentenceReplacements == null
                        ? null
                        : sentenceReplacements.get(tokenPosition);
                if (replacement == null) {
                    CoreLabel token = tokens.get(tokenPosition - 1);
                    resolved.append(token.word()).append(token.after());
                    tokenPosition++;
                    continue;
                }

                CoreLabel firstToken = tokens.get(tokenPosition - 1);
                String replacementText = replacement.text;
                if (!firstToken.originalText().isEmpty()
                        && Character.isUpperCase(firstToken.originalText().charAt(0))) {
                    replacementText = capitalize(replacementText);
                }
                CoreLabel lastToken = tokens.get(replacement.endIndex - 2);
                resolved.append(replacementText).append(lastToken.after());
                tokenPosition = replacement.endIndex;
            }
        }
        return resolved.toString();
    }

    private Map<Integer, Map<Integer, Replacement>> buildReplacements(
            Map<Integer, CorefChain> corefs,
            List<CoreMap> sentences) {
        Map<Integer, Map<Integer, Replacement>> replacements = new HashMap<>();
        if (corefs == null) {
            return replacements;
        }

        for (CorefChain chain : corefs.values()) {
            if (chain.getMentionsInTextualOrder().size() < 2) {
                continue;
            }
            CorefMention representative = chain.getRepresentativeMention();
            for (CorefMention mention : chain.getMentionsInTextualOrder()) {
                if (sameMention(mention, representative)) {
                    continue;
                }
                CoreLabel head = sentences.get(mention.sentNum - 1)
                        .get(TokensAnnotation.class)
                        .get(mention.headIndex - 1);
                String pos = head.get(PartOfSpeechAnnotation.class);
                if (!"PRP".equals(pos) && !"PRP$".equals(pos)) {
                    continue;
                }

                String replacementText = representative.mentionSpan;
                if ("PRP$".equals(pos) && !replacementText.endsWith("'s")) {
                    replacementText += "'s";
                }
                replacements
                        .computeIfAbsent(mention.sentNum, ignored -> new HashMap<>())
                        .put(mention.startIndex, new Replacement(mention.endIndex, replacementText));
            }
        }
        return replacements;
    }

    private static boolean sameMention(CorefMention left, CorefMention right) {
        return left.sentNum == right.sentNum
                && left.startIndex == right.startIndex
                && left.endIndex == right.endIndex;
    }

    private static String capitalize(String value) {
        if (value.isEmpty() || Character.isUpperCase(value.charAt(0))) {
            return value;
        }
        return Character.toUpperCase(value.charAt(0)) + value.substring(1);
    }

    private static final class Holder {
        private static final NLP INSTANCE = new NLP();
    }

    private static final class Replacement {
        private final int endIndex;
        private final String text;

        private Replacement(int endIndex, String text) {
            this.endIndex = endIndex;
            this.text = text;
        }
    }
}
