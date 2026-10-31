import json, sys
SECRET_IDS = {10, 898, 903, 908}
needles = [s.lower() for s in sys.argv[1:]]
for line in open('data/chats/vale-x-altr.jsonl'):
    m = json.loads(line)
    t = (m.get('text') or '')
    if m['id'] in SECRET_IDS:
        continue
    for n in needles:
        if n in t.lower():
            print(m['id'], m['ts'][:10], m.get('sender'), '|', t[:160].replace('\n', ' / '))
            break
