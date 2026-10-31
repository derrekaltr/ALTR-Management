"""Ad-hoc CS-gap metrics for haileigh-cox-x-altr (2026-09-18 run)."""
import json
import datetime
import re

PATH = 'data/chats/haileigh-cox-x-altr.jsonl'
CLIENT = 'Hailey Client'
# automated / templated broadcast senders + recognisable templates
AUTOMATED = ('Haleighcox takedown update', 'leak removal', 'Takedown Update',
             'Total Infringements Removed', 'reel inspo', 'reel ideas',
             'here’s your reel', 'reel | ideas')

PROMISE = re.compile(
    r"(let me (check|confirm|touch base|ask|see|find out|get back)|i'?ll (get|check|have|send|let you know|reach|relay|forward|make sure|put together|add|create|keep you|be on the lookout|update)"
    r"|we'?ll (get|be|have|send|keep|set|look|start|make)|will (check|reach out|update|keep you|be on the lookout)"
    r"|working on it|standby|we are actively working|get back to you|keep you updated|keep you posted"
    r"|shortly|asap|i promise|100% most definitely|we will have|coming up|next week)",
    re.I)

msgs = []
for line in open(PATH):
    d = json.loads(line)
    if d.get('service'):
        continue
    d['dt'] = datetime.datetime.fromisoformat(d['ts'])
    msgs.append(d)

team = [m for m in msgs if m['sender'] != CLIENT]

# longest stretch with zero *non-templated* outbound from our side
human = [m for m in team
         if not any(k.lower() in (m.get('text') or '').lower() for k in AUTOMATED)]
gaps = sorted(((b['dt'] - a['dt']).days, str(a['dt'].date()), str(b['dt'].date()))
              for a, b in zip(human, human[1:]))
print('longest zero-human-outbound stretches:', gaps[-8:])

allgaps = sorted(((b['dt'] - a['dt']).days, str(a['dt'].date()), str(b['dt'].date()))
                 for a, b in zip(team, team[1:]))
print('longest zero-any-outbound stretches:', allgaps[-5:])

promises = [m for m in team if PROMISE.search(m.get('text') or '')]
print('team messages containing forward-looking commitment language:', len(promises))
for m in promises:
    print('  ', m['dt'].strftime('%Y-%m-%d'), m['id'], m['sender'], '|',
          (m.get('text') or '')[:100].replace('\n', ' '))
