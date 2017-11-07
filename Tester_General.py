import re

text = "-1"


def valueFromText(text):
    return float(str(text))


def textFromValue(value):
    string = "{:g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string


value = valueFromText(text)

print(textFromValue(value))
