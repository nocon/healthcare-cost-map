import StringIO
from PyPDF2.pdf import ContentStream
from PyPDF2.generic import TextStringObject, ByteStringObject
from decimal import Decimal


def get_domain(domain):
    return domain.replace('http://', '').replace(
        'https://', '').split(':', 1)[0].split('/', 1)[0]


def get_regex(url):
    return '^' + url\
        .replace('$', '\$')\
        .replace('+', '\+')\
        .replace('&', '\&')\
        .replace('?', '\?')\
        .replace('ITERATOR', '(\d+)')\
        + '$'


def decode_pdf(pdf):
        try:
                from PyPDF2 import PdfFileReader
        except ImportError:
                print "Needed: easy_install pyPdf"
                raise

        stream = StringIO.StringIO(pdf)
        reader = PdfFileReader(stream)

        text = u""

        for page in range(reader.getNumPages()):
                text += extractText(reader.getPage(page))

        text_file = open("Output.txt", "w")

        text_file.write(pdf)

        text_file.close()
        return text


def extractText(page):
        text = u""
        content = page["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, page.pdf)
        # Note: we check all strings are TextStringObjects. ByteStringObjects
        # are strings where the byte->string encoding was unknown, so adding
        # them to the text here would be gibberish.
        for operands, operator in content.operations:
            if operator == "Tj":
                _text = operands[0]
                text += '\n'
                if isinstance(_text, TextStringObject):
                    text += _text
            elif operator == "T*":
                text += "\n"
            elif operator == "'":
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == '"':
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == "TJ":
                text += '\n'
                for i in operands[0]:
                    if isinstance(i, ByteStringObject):
                        text += i
                    elif isinstance(i, TextStringObject):
                        text += i
        return text


def is_a_phone_number(s):
    if s.strip()[0] == "0":
        return True
    if '(' in s:
        return True
    if not '+' in s and not '-' in s and count_digits(s) > 8:
        return True
    return False


def get_decimal(s):
    if s == '':
        return None
    #Decimal mark is comma
    elif len(s) > 3 and s[len(s)-3] == ',':
        return Decimal(s.replace(',', '.')).quantize(Decimal("0.00"))
    #Decimal mark is dot
    else:
        return Decimal(s.replace(',', '')).quantize(Decimal("0.00"))


def count_digits(s):
        count = 0.0
        for i in s:
            if i.isdigit():
                count += 1
        return count


def replace_insensitive(string, target, replacement):
    no_case = string.lower()
    index = no_case.find(target.lower())
    if index > 0:
        result = string[:index] + replacement + string[index + len(target):]
        return result
    else:
        return string


def remove_format_characters(text):
    return text.replace(u"\xa0", '').replace('\r', '')\
        .replace('\n', '').replace('\t', '')


def find_most_common_tag(soup):
    tags = dict()
    for tag in soup.findAll():
        if tag.name == 'div' or tag.name == 'p' or tag.name == 'td':
            if tag.name in tags:
                tags[tag.name] += 1
            else:
                tags[tag.name] = 1
    return max(tags, key=tags.get)
