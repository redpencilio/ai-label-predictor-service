import re

class Preprocessor:
    def __init__(self):
        regex_transformations = [
            (r'[,-.?!_\[\]\\()\'\"]', ""),
            (r'[â]', ""),
            (r'(<.*>.*</.*>)', ""),
            (r'[0-9]*', ""),
            (r'[\r\n]+', ""),
            (r'\s+', " "),
            (r'[ \t]+$', ""),
            (r'^\s+', "")
        ]
        self.regex_transformations = regex_transformations

    def preprocess(self, value):
        value = value.lower()
        for regex, value_to_replace_with in self.regex_transformations:
            value = re.sub(regex, value_to_replace_with, value)
        return value

    def __call__(self, *args, **kwargs):
        return self.preprocess(*args, **kwargs)
