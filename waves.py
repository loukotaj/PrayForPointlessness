WAVES = [
    # ───── EARLY GAME – single‑shape, tier‑1 ─────
    {
        "steps": [  {"type": "triangle", "tier": 1, "count": 4} ],
        "reward": 10,
        "spawn_rate": 75,          # frames between spawns
    },
    {
        "steps": [  {"type": "square",   "tier": 1, "count": 4} ],
        "reward": 12,
        "spawn_rate": 72,
    },
    {
        "steps": [  {"type": "star",     "tier": 1, "count": 4} ],
        "reward": 14,
        "spawn_rate": 70,
    },

    # ───── MIXED TIER‑1 ─────
    {
        "steps": [
            {"type": "triangle", "tier": 1, "count": 5},
            {"type": "square",   "tier": 1, "count": 3},
        ],
        "reward": 18,
        "spawn_rate": 68,
    },
    {
        "steps": [
            {"type": "square",   "tier": 1, "count": 4},
            {"type": "star",     "tier": 1, "count": 4},
        ],
        "reward": 22,
        "spawn_rate": 66,
    },

    # ───── FIRST TIER‑2 ENEMIES ─────
    {
        "steps": [
            {"type": "triangle", "tier": 2, "count": 4},
            {"type": "square",   "tier": 1, "count": 4},
            {"type": "star",     "tier": 1, "count": 2},
        ],
        "reward": 26,
        "spawn_rate": 62,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 2, "count": 5},
            {"type": "square",   "tier": 2, "count": 3},
            {"type": "star",     "tier": 1, "count": 3},
        ],
        "reward": 32,
        "spawn_rate": 60,
    },

    # ───── MID GAME – more bodies & tier‑2/3 mix ─────
    {
        "steps": [
            {"type": "triangle", "tier": 2, "count": 6},
            {"type": "square",   "tier": 2, "count": 4},
            {"type": "star",     "tier": 2, "count": 4},
        ],
        "reward": 40,
        "spawn_rate": 56,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 3, "count": 4},
            {"type": "square",   "tier": 2, "count": 5},
            {"type": "star",     "tier": 2, "count": 5},
        ],
        "reward": 48,
        "spawn_rate": 54,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 3, "count": 6},
            {"type": "square",   "tier": 3, "count": 4},
            {"type": "star",     "tier": 2, "count": 4},
        ],
        "reward": 58,
        "spawn_rate": 52,
    },

    # ───── LATE GAME – tier‑3/4 swarms ─────
    {
        "steps": [
            {"type": "triangle", "tier": 3, "count": 8},
            {"type": "square",   "tier": 3, "count": 6},
            {"type": "star",     "tier": 3, "count": 4},
        ],
        "reward": 72,
        "spawn_rate": 48,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 6},
            {"type": "square",   "tier": 3, "count": 6},
            {"type": "star",     "tier": 3, "count": 6},
        ],
        "reward": 85,
        "spawn_rate": 46,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 6},
            {"type": "square",   "tier": 4, "count": 6},
            {"type": "star",     "tier": 3, "count": 6},
        ],
        "reward": 100,
        "spawn_rate": 44,
    },

    # ───── END GAME – full tier‑4 assault ─────
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 8},
            {"type": "square",   "tier": 4, "count": 8},
            {"type": "star",     "tier": 4, "count": 6},
        ],
        "reward": 120,
        "spawn_rate": 42,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 10},
            {"type": "square",   "tier": 4, "count": 10},
            {"type": "star",     "tier": 4, "count": 10},
        ],
        "reward": 150,
        "spawn_rate": 38,
    }
]
