"""Match glossary labels and the original Russian Spawn imperative."""
import re


def keyword_mentioned(label, text):
    # The Beta glossary uses the infinitive, card rules use the imperative.
    # Keep other labels exact: arbitrary stemming also matches unrelated words.
    forms = [label]
    if label.casefold() == 'создать':
        forms += ['создайте', 'создай', 'создавайте', 'создавай']
    return bool(label and re.search(r'(?<!\w)(?:' + '|'.join(map(re.escape, forms)) + r')(?!\w)', text, re.I))
