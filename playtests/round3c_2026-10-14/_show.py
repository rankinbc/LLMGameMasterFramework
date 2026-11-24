import json,sys
d=json.load(sys.stdin)
print(d['verdict']); print('\n'.join(d['flags'])); print('\n'.join(d['warnings'])); print(d['random']['win'],d['heuristic']['win'],d['lookahead']['win'], d.get('tuning_round')); print(d.get('mutation')); print(d.get('note'))
