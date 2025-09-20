import re

def find_numbers():
    """
    Finds all numbers in the given text and returns them as a list.
    """
    text = r'invoices: 123, 4567, and #8900 are due by the end of the month.'
    # Regular expression to match numbers
    pattern = r'\b\d+\b'
    return re.findall(pattern, text)

def find_capitals():

    """
    Finds all capitalized words in the given text and returns them as a list.
    """
    text = r'The Quick Brown Fox Jumps Over The Lazy Dog.'
    # Regular expression to match capitalized words
    pattern = r'\b[A-Z][a-z]*\b'
    return re.findall(pattern, text)

def find_date():
    """
    Find all month, 
    """
    text = r'The event is scheduled for 12/31/2023 and 01/01/2024.'
    # Regular expression to match dates in MM/DD/YYYY format
    pattern = r'\d{2}/\d{2}/(?P<year>\d{4})'
    return re.findall(pattern, text)

def find_spaces():
    text = r'This   is      a           test            text            with                multiple spaces.'
    # Regular expression to match multiple spaces
    replacement = ' '
    pattern = r'\s+'
    # pattern = r' +'
    match = re.sub(pattern, replacement, text)
    return match

def removes_html_tags():
    """
    Removes HTML tags from the given text.
    """
    text = r'<html><body><h1>Title</h1><p>This is a paragraph.</p></body></html>'
    # Regular expression to match HTML tags
    pattern = r'<[^>]+>'
    return re.sub(pattern, '', text)

def backref1():
    text = r'text with test test and 5th and' \
    'test test and 5th and test test and 5th and' \
    'more  no duplicate duplicate test test and 5th and' \
    'test test and 5th and test test and 5th and' \
    'in here'
    pattern = re.compile(r'\b(?P<word>\w+)\s+(?P=word)\b', re.IGNORECASE)
    matches = pattern.finditer(text)
    for match in matches:
        print(f"Found '{match.group(0)}' at position {match.start()}-{match.end()}")



print(find_numbers())
print(find_capitals())
print(find_date())
print(find_spaces())
print(removes_html_tags())
backref1()