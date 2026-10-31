import json

P = 'data/analysis/cs-gaps-2026-09-25/sarah-x-altr.json'
d = json.load(open(P))
req = ['responsiveness', 'follow_through', 'proactive_communication', 'onboarding_handoff',
       'chatter_conduct', 'platform_health', 'billing_ops', 'ownership_escalation',
       'disengagement_detection', 'security_hygiene']
assert set(d['dimensions']) == set(req), set(req) ^ set(d['dimensions'])
for k in req:
    v = d['dimensions'][k]
    assert v['severity'] in (0, 1, 2, 3)
    assert v['internal_failure']
    assert 2 <= len(v['evidence']) <= 3, (k, len(v['evidence']))
    for e in v['evidence']:
        assert set(e) == {'quote', 'who', 'date'}, e
        assert len(e['date']) == 10
print('OK — 10 dimensions, evidence well-formed')
print('status', d['status'], '| last_client_message', d['last_client_message'])
print('severities', {k: d['dimensions'][k]['severity'] for k in req})
print('metrics', {k: v for k, v in d['metrics'].items() if k != 'method'})
