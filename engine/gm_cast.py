"""gm_cast: a named cast the engine owns, so "who died" has one true answer.

The /play STORY roll decides whether a game has a cast (3: cast, 4: saga). When it does, the engine builds the
roster in init_state and keeps it in s["cast"], and every loss of people goes through `fall`, which decides which
named people were among the lost. The GM narrates from s["cast"] and the events; it never invents a name.

    from gm_cast import roster, fall, fallen_text, alive

    def init_state(self, rng):
        s = {...}
        s["cast"] = roster(rng, 5, "military", roles=["sergeant", "gunner", "scout", "cook", "drummer"])
        return s

    # when the company loses `lost` of its `men`:
    dead = fall(s, rng, lost, pool=s["men"] + lost)      # the named people among the lost (maybe none)
    if dead:
        ev.append(fallen_text(dead))                      # "Sergeant Reyle and Orrin fell."
    # a unit-scale game (each loss is one person): fall(s, rng, lost) with no pool kills `lost` cast members.

A cast entry is a plain dict: {"name", "role", "tell", "alive", "fell"}. It is JSON-safe and visible to the player;
nothing in it is a rule, so it is not TRACKED and never appears on the status line or the sheet.
"""

# First and last names by setting family. Short, pronounceable, no real famous people. A pool of 24 x 24 gives
# hundreds of distinct names per family, so two games rarely share one.
_FIRST = {
    "military": "Tomas Pell Dov Anja Rurik Hesse Mara Odo Brann Lisel Caius Ferro Ilse Jory Sten Wenna Garet Noor Piet Rusk Elin Tavi Konn Bryd".split(),
    "historical": "Aldo Bess Corin Dinah Edric Fenna Gil Hester Ivo Jess Kit Lora Mungo Nell Osric Phebe Quill Rowan Sibyl Tam Una Wat Ysolt Zeb".split(),
    "fantasy": "Arlo Brisa Cadoc Delph Eirlys Fenwick Gwil Hollis Idony Jareth Kestrel Lio Maelis Nyx Orrin Perrin Quenby Rhoswen Sefa Thane Ulla Varek Wren Yann".split(),
    "scifi": "Ada Bex Cole Dara Enzo Faye Gus Hana Ike Juno Kai Lux Milo Nia Otto Pria Quinn Rae Sol Tess Uri Vee Wes Zia".split(),
    "nature": "Scar Moss Bramble Flint Dusk Reed Pebble Nettle Rook Ash Fern Tallow Burr Clover Mire Sedge Thistle Wick Larch Shale Sorrel Hob Tansy Vole".split(),
    "workplace": "Alma Ben Carla Des Erin Felix Gina Hal Ines Jo Kurt Lena Max Nora Omar Pat Rosa Sam Tia Umar Val Wes Yuki Zane".split(),
    "abstract": "One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Ace Bell Chip Dot Echo Fold Grid Hook Inch Jot Knot Loop".split(),
}
_LAST = {
    "military": "Reyle Orrin Kasker Vance Dorn Hallam Brecht Soller Marrow Quist Tern Ashby Varga Pell Rook Stroud Hale Ingram Fenn Coyle Marsh Teague Wyck Larkin".split(),
    "historical": "Abbott Blythe Carver Dunne Elwood Fairley Gosse Harrow Inch Jessop Kemble Lowry Marlow Nance Orme Pryor Quarrie Rudd Sayer Thorne Underhill Voss Wilde Yates".split(),
    "fantasy": "Ashvane Brackwater Coldmere Duskwell Emberly Fallow Greyhallow Hartswood Irongate Kettleby Longshadow Mossbank Nightbrook Oakhollow Pendle Quickwater Ravensholm Saltmarch Thornfield Underbough Vellmoor Wintermere Yarrow Zell".split(),
    "scifi": "Okafor Lindqvist Tanaka Reyes Novak Achebe Castellan Dube Eriksen Farouk Ghosh Halvorsen Ito Juarez Kowalski Lemaire Mbeki Nakamura Osei Petrov Quintero Rask Sato Varga".split(),
    "nature": "of-the-Bank of-the-Reeds Three-Toe One-Ear Longtail Greyback Half-Wing Broadfoot Quickfoot Sharp-Eye Low-Branch Deepburrow Highnest Brightfin Dullclaw Stillwater Nightcall Dawnrunner Hollowlog Stonebed Mudwalker Treetop Riverbend Windward".split(),
    "workplace": "Adler Brooks Chen Diaz Evans Fischer Grant Hughes Iqbal Jensen Khan Lopez Murray Nguyen Ortiz Price Reid Singh Torres Usman Vogel Walsh Young Zimmer".split(),
    "abstract": "Prime Minor Major Sharp Flat Grave Acute Plain Round Square Oblong Oblique Even Odd Null Whole Half Quarter Dual Triple Spare Fixed Loose Late".split(),
}
_FAMILY_ALIAS = {"other": "workplace", "historical": "historical"}

# one tell each: a habit the GM can show in half a line, never a rule
_TELLS = (
    "counts everything twice", "sings on watch", "owes money in every port", "never sits with their back to a door",
    "keeps a list of the dead", "laughs at the wrong moments", "writes letters nobody sends", "sharpens things when nervous",
    "talks to the animals", "has a bad knee and hides it", "knows every rumor first", "prays quietly before anything risky",
    "cheats at cards and loses anyway", "carries a child's drawing", "cannot swim", "remembers every name",
    "volunteers for everything", "argues with the maps", "eats standing up", "mends other people's gear",
    "has been here before and will not say when", "keeps the last bottle for the end", "whistles the same four notes",
    "says 'nearly there' every hour", "was somebody once", "trusts nobody over the rank of captain", "collects small stones",
    "sleeps through anything", "is the only one who can read the old script", "has a brother on the other side",
)


def _pools(family):
    fam = _FAMILY_ALIAS.get(family, family)
    if fam not in _FIRST:
        fam = "workplace"
    return _FIRST[fam], _LAST[fam]


def roster(rng, n, family="workplace", roles=None, tells=True):
    """n distinct named people for this setting family. `roles` labels them in order (cycled if short).
    Deterministic for a given rng, so the seed decides the cast."""
    first, last = _pools(family)
    surnames = set()
    cast = []
    tell_pool = list(_TELLS)
    rng.shuffle(tell_pool)
    for i in range(n):
        for _ in range(50):  # lit-ok: bounded retry for a distinct surname, since events name people by it
            given, surname = rng.choice(first), rng.choice(last)
            if surname not in surnames:
                break
        surnames.add(surname)
        name = f"{given} {surname}"
        role = (roles[i % len(roles)] if roles else "hand")
        cast.append({"name": name, "role": role, "tell": tell_pool[i % len(tell_pool)] if tells else "", "alive": True, "fell": None})
    return cast


def alive(s):
    return [c for c in s.get("cast") or [] if c.get("alive")]


def fall(s, rng, lost, pool=None, turn=None):
    """Decide which named people were among `lost` casualties. With `pool` (the headcount before the loss) each
    living cast member is lost with probability lost/pool; without it, each loss is one cast member, in random order.
    Marks them dead in s["cast"] and returns them. Never kills more than are alive or more than were lost."""
    living = alive(s)
    if lost <= 0 or not living:
        return []
    dead = []
    if pool:
        p = min(1.0, lost / max(1, pool))
        for c in living:
            if len(dead) >= lost:
                break
            if rng.chance(p):
                dead.append(c)
    else:
        order = list(living)
        rng.shuffle(order)
        dead = order[:lost]
    for c in dead:
        c["alive"] = False
        c["fell"] = turn if turn is not None else s.get("_turn")
    return dead


def _short(c):
    """'Sergeant Reyle' for the first mention, by role and surname."""
    surname = c["name"].split()[-1]
    role = c.get("role") or ""
    return f"{role[:1].upper()}{role[1:]} {surname}".strip()


def fallen_text(dead, verb="fell"):
    """'Sergeant Reyle fell.' or 'Sergeant Reyle and Scout Orrin fell.' Empty string for no one."""
    if not dead:
        return ""
    names = [_short(c) for c in dead]
    who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return f"{who} {verb}."


def names(s, living_only=True):
    return [c["name"] for c in (alive(s) if living_only else s.get("cast") or [])]
