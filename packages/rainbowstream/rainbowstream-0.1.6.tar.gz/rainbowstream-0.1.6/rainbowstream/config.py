import json
import re
import os
import os.path


# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)


def load_config(filepath):
    """
    Load config from filepath
    """
    with open(filepath) as f:
        content = ''.join(f.readlines())
        match = comment_re.search(content)
        while match:
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
    return json.loads(content)

# Load default colorset
c = {}
default_config = os.path.dirname(__file__) + '/colorset/default.json'
data = load_config(default_config)
for d in data:
    c[d] = data[d]
c['theme'] = 'default'
# Load user's colorset
rainbow_config = os.environ.get(
    'HOME',
    os.environ.get(
        'USERPROFILE',
        '')) + os.sep + '.rainbow_config.json'
try:
    data = load_config(rainbow_config)
    for d in data:
        c[d] = data[d]
    c['theme'] = 'custom'
except:
    pass
