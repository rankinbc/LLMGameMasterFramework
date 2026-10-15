# Hired Knives

Rolls: FORM=6 pursuit, SET=24 restaurant kitchen Friday night, ROLE=12 mercenary captain, LOOP=18 capture and hold nodes, CLOCK=6 rival racing to the same prize, TWIST=37 information one turn late, WIN=2 reach a location and get out, MAP=11 weekly calendar grid 7x3, TONE=2 dry humor.

Fingerprint: actions = take, raid, push, reinforce, hire, hold, comp, leak, walkout, stiff. Tracked numbers = Cash, Cooks (spare of total), Kitchens held (list with cooks and stars).

## Rulesheet
1. High Street has 7 kitchens in a row. You hold a kitchen with 2 cooks; a 3rd cook makes it hard to raid and easier to cook in. Rooney's Copper Pans hold kitchens too.
2. 21 services, Saturday lunch to Friday late. One action per service. Each kitchen you hold pays 4 a service, each cook costs 1; if you cannot pay, a cook walks.
3. Volk the critic eats dinner at the loudest kitchen (highest Buzz) she has not tried yet. Ties are her secret, and she has one habit her column hints at.
4. If she eats in your kitchen: d6, need 4+ (3+ with 3 cooks). Success: a star (a 6 is two) and +6 cash. Fail: Buzz -2.
5. News is one service late: the Buzz board, where Volk ate, and Rooney's moves. Your own kitchen's rolls, and raids on you, you see at once. Taking or raiding a kitchen whose holder changed since the board was printed wastes the service.
6. Actions: Take a house kitchen (8 cash, 2 spare cooks), Raid one of Rooney's (2 spare cooks, d6 need 5+, 4+ with 3 spare; a failed raid loses a cook), Push Buzz +2 (4 cash), Reinforce (3rd cook), Hire a cook (6 cash).
7. Friday dinner Volk returns to the kitchen with the most stars (tie: loudest). Hold it and pass the service: 3+ if you earned its star, else 4+. Then walk out paying 2 per cook.
8. Lose if Rooney feeds her Friday or she eats elsewhere. Two failed rolls in a row open Comp the Room. From Wednesday Rooney pushes harder, raids your starred kitchens on Thursday and Friday lunch, and her habit is for sale (6).

## Signature detail
Volk has one hidden habit per game (walker: within two doors of last night; hype: ignores a kitchen whose Buzz rose 4+ since her last dinner; noon: judges Buzz as it stood at the end of lunch). Her column hints at it Saturday late and Tuesday late; the sub-editor sells it outright from Wednesday for 6. The Buzz board the player sees is one service stale, so a take or raid can bounce off a kitchen whose holder changed.

## Midpoint plan
Turn 11 (Wednesday dinner): Rooney's pushes go from +1 to +2; Thursday lunch he raids the player's best starred kitchen (5+, 6+ if reinforced), and his raiders come out of his quietest kitchen, which reverts to the house. Unlock: Leak (6 cash) reveals Volk's habit in plain words. Friday lunch Rooney grabs or raids whatever kitchen has the most stars.

## Rival policy (one line)
Rooney expands next door to his loudest kitchen up to three, pushes his loudest unvisited kitchen every service (+1, +2 from Wednesday), raids the player's best starred kitchen Thursday and Friday lunch, and spends Friday dinner at the pass.

## Selftest tuning log
| run | change | random win | heuristic win | flags |
|---|---|---|---|---|
| 1 | first draft (after fixing a stale-take crash into a bounce) | 0.06 | 0.11 | TOO HARD |
| 2 | takings 3 to 4; Rooney push +1 (+2 from Wed); raids Thu only mid-week; Rooney Friday push aimed at star kitchen; heuristic reserves exit bonus; stale raid defaults fixed | 0.10 | 0.19 | TOO HARD |
| 3 | Rooney service 5+ (was 4+); start cash 24 | 0.15 | 0.22 | TOO HARD |
| 4 | Rooney raiders come from his quietest kitchen (reverts to house); hire 6; heuristic reinforces starred kitchens Wed-Thu and pushes Fri dinner | 0.13 | 0.27 | TOO HARD |
| 5 | heuristic hires ahead for Friday | 0.13 | 0.27 | TOO HARD |
| 6 | Rooney never raves (1 star max); Rooney does not push Friday dinner | 0.16 | 0.37 | none |
| 7 | removed unstated +1 Buzz on Volk visit, vestigial keys | 0.16 | 0.36 | none |
