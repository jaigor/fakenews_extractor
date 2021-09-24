import os
from pathlib import Path
import xml.etree.ElementTree as ET

author_ids = {}
# Reading in English meta data (spreader or not)
with open('pan20-author-profiling/test/es.txt', "r") as r:
    data = r.read().split("\n")

    for line in data:
        l = line.split(":::")
        if len(l) > 1:
            print(l[0] + " " + str(l[1]))
            author_ids[l[0]] = l[1]  # id, yes or no

# Reading in and concatenating English tweets
pathlist = Path('pan20-author-profiling/test/es/').glob('**/*.xml')
for path in pathlist:  # iterate files
    print(path)
    head, tail = os.path.split(path)
    t = tail.split(".")
    author = t[0]

    path_in_str = str(path)
    tree = ET.parse(path_in_str)
    root = tree.getroot()
    for child in root:
        print(author_ids[author])
        if author_ids[author] == '1':
            spread = 'yes'
        else:
            spread = 'no'

        with open('pan20-author-profiling/texts/test/es/' + spread + '/' + author + '.txt', 'w') as f:
            xi = []
            for ch in child:
                xi.append(ch.text)
            content = ' '.join(xi)
            f.write(content)
