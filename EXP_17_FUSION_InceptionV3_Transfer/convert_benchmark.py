import sys
import json
import pickle

for files in sys.argv[1:]:
  if '.txt' not in files:
    continue
  with open(files, 'r') as r, open(files.replace('.txt', '.pkl'), 'wb') as w:
    lines = r.readlines()
    lines = [lines[i] for   i in range(6, len(lines), 7)]
    lines = [json.loads(l.replace("'", '"')) for l in lines]
    pickle.dump(lines, w)
      