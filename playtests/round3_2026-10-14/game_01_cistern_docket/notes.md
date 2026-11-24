# Cistern Docket

Premise: the Collegium's cisterns are draining and the Bursar's office has frozen the budget until someone is named. The cafe owner hears every rumor on the three isles, so the docket lands on her napkin.

## Rolls
FORM=17 (triage) SET=30 (wizard academy budget office) ROLE=45 (cafe owner) LOOP=8 (gather, craft, upgrade one tool) CLOCK=11 (water table drops) TWIST=30 (character slowly transforming) WIN=15 (name the culprit with two pieces of evidence) MAP=7 (three islands and the sea) TONE=6 (military procedural) CURRENCY=11 (Evidence)

## Rulesheet
Printed by `python engine.py rules` (built from CONSTANTS).

## Signature detail
The cafe owner turns into a heron on a fixed schedule: Webbed at night 4 (free ferries), Heron at night 8 (cafe closes, stakeouts open). The siphon's habit (ring up, ring down, or busiest isle) is hidden and learned from where it has struck.

## Midpoint plan
Night 8: Heron (cafe desk closes, stakeout lever opens). Night 10: the hearing opens (naming allowed). Night 11: the aquifer cracks (Water falls 2 a night).

## Rival policy
The siphon strikes one isle a night: ring habits step the isle by +1 or +2, the third habit takes the isle with the most waiting reports. Tell comes after the strike, never before.

## Tuning
check rounds: 4 of 4 (CLEAN at round 3 and round 4). Known rough edges: look-ahead 92 percent (over the 90 percent band by 0.02); check and bind are marginal in ablation; miss and cleared_tip tags are rare.
After play: the heuristic now names when the water cannot outlast another night (it used to cross-check and die), and labels say '1 piece'. Verified with check --quick and selftests (heuristic 0.44, look-ahead 0.93).
