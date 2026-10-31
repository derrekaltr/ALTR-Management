import os, glob, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pats = sys.argv[1:] or ["incredible first week", "are you single", "new to telegram still", "Copy the domain exactly"]
files = glob.glob(os.path.join(ROOT, "data/chats/*.jsonl")) + [f for f in glob.glob(os.path.join(ROOT, "data/weeks/**/*"), recursive=True) if os.path.isfile(f)]
for f in files:
    try:
        t = open(f, errors="ignore").read()
    except Exception:
        continue
    for p in pats:
        for m in re.finditer(re.escape(p), t, re.I):
            print(os.path.relpath(f, ROOT), "|", t[max(0, m.start() - 60): m.end() + 160].replace("\n", " "))
            break
