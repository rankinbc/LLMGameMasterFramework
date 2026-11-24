# Hail Term - session notes

Title: Hail Term
Rolls: FORM=17 SET=60 ROLE=27 LOOP=21 CLOCK=3 TWIST=37 WIN=18 MAP=8 TONE=2
Seed: 44618

Rulesheet
1. Each turn do one thing: send the students to one storm, hold a tuition day (+12 cash), or buy gear. Wages cost 3 a turn.
2. Storms queue over six districts. A storm that has waited 2+ turns costs 1 approval a turn. The board holds 3; a fourth pushes the oldest out for -3 approval.
3. A storm has a layer 1 to 3. Sending rolls d6, need layer+2. Success pays 8/14/22 cash and +5/+7/+10 approval. Fail: -2 approval, storm stays.
4. Each turn a waiting storm may deepen one layer (1 in 3; 1 in 2 from turn 10): richer, harder. Layer 4 bursts: -6 approval, storm gone.
5. Reports are a day old: a storm's shown layer is last turn's, and new storms show "?". Students on site learn the true layer.
6. Pell's cloud-seeding wagon names the longest-waiting storm that has sat a day; next turn he takes it if it is still there (-2 approval, no pay).
7. Gear ladder: kites 20, barometer 20 (+1 to every roll each), then from turn 10 the semaphore line 35 (reports same day). From turn 10 storms come faster.
8. The bank takes 60 cash as turn 14 opens. Cash below 0 or approval 0 closes the school. After two failed sends old Agnes clears the longest-waiting storm for 12. Win: approval 70+ after turn 20.

Signature detail: storms are a day-old report. The board shows yesterday's layer; the students find out the truth when they arrive. Old Agnes, the retired headmistress, does not do invoices.
Midpoint plan: turn 10 is storm season (second storm 50 percent a turn, deepening 1 in 2) and unlocks the semaphore line (35) which removes the report lag. The bank's 60 lands as turn 14 opens.
Rival policy: Pell's cloud-seeding wagon names the longest-waiting storm that has sat at least a day; next turn he seeds it if it is still on the board (-2 approval, no fee for you).
Fingerprint: actions = send, tuition, gear, agnes; tracked = cash, approval, storm board (layer/age list).

Selftest rounds
1. random 0.00 / heur 0.00, heur turn_avg 8.3, flags TOO HARD + SHORT GAMES. Approval sinks far outran sources; heuristic parked on tuition for a 90 debt.
2. debt 90->60, approval 3/5/8 -> 4/6/9, arrivals 1+25% (season 1+60%), Pell only names storms that sat a day: random 0.00 / heur 0.00, heur turn_avg 13.4, same flags.
3. waiting cost only for storms aged 2+, wages 4->3, heuristic rewritten (kites early, tuition only when bank projection short): random 0.01 / heur 0.25, turn_avg 18.8, flag TOO HARD.
4. second-storm chance 15% / 50%, overflow -4 -> -3, heuristic 12-cash buffer: random 0.01 / heur 0.22, turn_avg 20.1, flag TOO HARD (heuristic over-tuitioned).
5. approval 5/7/10, heuristic projects +4/turn: random 0.03 / heur 0.44, turn_avg 19.6, early_end 0.02, no flags. Confirmed after docstring-only edits: identical numbers.
