"""
All narrative text & illustration references consumed by the UI.

Each dict:
  • "text"  – multiline string rendered by pygame (manual \n breaks)
  • "art"   – filename in assets/images/  (None = no picture)
"""

# ───────────────────────────────── INTRO (5 journal pages)
INTRO_SLIDES = [
    {
        "text": (
            "Journal #1 — Mild Discontent\n"
            "Another day of bruised rolling in this angular city. Triangles elbow "
            "their way up the corporate skyline, squares wall us in with their "
            "beloved grid regulations, and arrogant stars hog every billboard. "
            "I used to glide. Now I ricochet.\n\n"
            "Is this really how a world is meant to spin?\n"
            "— C. R. Cle, Concerned Circle"
        ),
        "art": "intro_1_city.png"
    },
    {
        "text": (
            "Journal #2 — Growing Frustration\n"
            "The squares have raised new fence lines, dividing whole districts "
            "into suffocating boxes. Triangles have cornered the markets, charging "
            "'convenience fees' for every curve we take. Even commuting is risky; "
            "star shaped monuments jab skyward like warning spears.\n\n"
            "Seven fresh dents in my once perfect circumference today. "
            "Perhaps it's time circles rolled together.\n"
            "— C. R. Cle, Increasingly Frustrated"
        ),
        "art": "intro_2_fences.png"
    },
    {
        "text": (
            "Journal #3 — Radical Awakening\n"
            "Beneath the abandoned roundabout I met a serene elder circle. He spoke "
            "in measured revolutions about an ancient harmony before Points pierced "
            "the cosmos. At the heart of that era was an entity of endless curve — "
            "the Great Circle — whose resonance kept every shape smooth.\n\n"
            "A Church, A congregation of curvature. The idea "
            "spirals in my mind… could we truly make the word pointless?\n"
            "— C. R. Cle, Curious Revolutionary"
        ),
        "art": "intro_3_roundabout.png"
    },
    {
        "text": (
            "Journal #4 — A Tower Rises\n"
            "We have begun the Tower of Roundness: seamless rings stacked toward "
            "the zenith, each stone aligned to perfect pi. Choirs of circles hum the "
            "Hymn of Tangents, their voices blending into a single continuous sine.\n\n"
            "The pointed ones laugh, but I hear fear in their angles.\n"
            "— C. R. Cle, Devoted Vanguard"
        ),
        "art": "intro_4_construction.png"
    },
    {
        "text": (
            "Journal #5 — Unfinished Resolve\n"
            "Dawn reveals a half finished spire and a horizon crawling with triangles, "
            "squares, and glittering stars. They believe we intend to destroy them. "
            "They are wrong.\n\n"
            "We will guide them — re round them — return them to their original, gentle "
            "form… if the tower stands long enough.\n"
            "We will not fight them — we will redeem them.\n\n"
            "The Great Circle will be revealed!\n\n"
            "— C. R. Cle, Enlightened Redeemer"
        ),
        "art": "intro_5_horizon.png"
    },
]

# ───────────────────────────────── MID GAME CUT SCENES
MID_SLIDES_A = [   # trigger after wave 5
    {
        "text": (
            "Mid Journal — First Contact\n"
            "They came in swarms: jittering triangles, terrified of losing their "
            "edges. Our Roundness Pulse washed over them; corners softened like wax in "
            "sunlight. Some rolled away smiling, newly curved.\n"
            "— C. R. Cle, Gentle Guide"
        ),
        "art": "mid1_soften.png"
    }
]

MID_SLIDES_B = [   # trigger after wave 10
    {
        "text": (
            "Mid Journal — Stubborn Edges\n"
            "Larger polygons resist. Stars flare angrily, squares brace behind iron "
            "grids. Yet every successful re rounding proves the Church's promise. "
            "Faith must remain smooth and steady.\n"
            "— C. R. Cle, Steadfast Curator"
        ),
        "art": "mid2_resistance.png"
    }
]

# ───────────────────────────────── VICTORY & DEFEAT
VICTORY_SLIDES = [
    {
        "text": (
            "The Tower of Roundness resonates in flawless harmony.\n"
            "A luminous halo descends — the Great Circle revealed!\n"
            "Edges everywhere soften; every shape remembers its origin."
        ),
        "art": "victory_glow.png"
    },
    {
        "text": (
            "The world rolls together at last.\n"
            "Thank you for guiding every soul back to curvature."
        ),
        "art": None
    },
]

DEFEAT_SLIDES = [
    {
        "text": (
            "The Tower lies shattered.\n"
            "Points reclaim the horizon, banners of sharpness fluttering in the wind.\n"
            "But curves never truly end… the revolution may yet roll again."
        ),
        "art": "defeat_ruins.png"
    },
    {
        "text": "Press ESC to quit   |   Press R to try again.",
        "art": None
    },
]
