from textblob import TextBlob


class TextProcessor:

    def __init__(self, text_to_process):
        self._text = text_to_process

    def extract_nouns(self):
        blob = TextBlob(self._text)
        return blob.noun_phrases
