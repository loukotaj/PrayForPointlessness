WAVES = [
    # ─────────────────────────── 1-5 : gentle ramp ──────────────────────────
    {   # a few more triangles to warm-up
        "steps": [ {"type": "triangle", "tier": 1, "count": 6} ],
        "reward": 10,
        "spawn_rate": 75,
    },
    {   # squares enter, triangles still around
        "steps": [
            {"type": "triangle", "tier": 1, "count": 3},
            {"type": "square",   "tier": 1, "count": 4},
        ],
        "reward": 12,
        "spawn_rate": 72,
    },
    {   # first stars, plus fodder triangles
        "steps": [
            {"type": "triangle", "tier": 1, "count": 4},
            {"type": "star",     "tier": 1, "count": 4},
        ],
        "reward": 14,
        "spawn_rate": 70,
    },
    {   # mixed tier-1 crowd
        "steps": [
            {"type": "triangle", "tier": 1, "count": 6},
            {"type": "square",   "tier": 1, "count": 4},
        ],
        "reward": 18,
        "spawn_rate": 68,
    },
    {   # slightly larger skirmish before tier-2 arrives
        "steps": [
            {"type": "triangle", "tier": 1, "count": 6},
            {"type": "square",   "tier": 1, "count": 6},
            {"type": "star",     "tier": 1, "count": 4},
        ],
        "reward": 22,
        "spawn_rate": 66,
    },

    # ────────────────────────── 6-10 : tier-2 era ───────────────────────────
    {
        "steps": [
            {"type": "triangle", "tier": 2, "count": 5},
            {"type": "square",   "tier": 1, "count": 4},   
            {"type": "star",     "tier": 1, "count": 2},
            {"type": "boss",     "tier": 1, "count": 1},
        ],
        "reward": 26,
        "spawn_rate": 62,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 2, "count": 6},
            {"type": "square",   "tier": 2, "count": 4},
            {"type": "star",     "tier": 1, "count": 4},   
        ],
        "reward": 32,
        "spawn_rate": 60,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 2, "count": 8},
            {"type": "square",   "tier": 2, "count": 6},
            {"type": "star",     "tier": 2, "count": 4},
            {"type": "triangle", "tier": 1, "count": 4},   
        ],
        "reward": 40,
        "spawn_rate": 56,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 3, "count": 4},
            {"type": "square",   "tier": 2, "count": 6},
            {"type": "star",     "tier": 2, "count": 6},
            {"type": "triangle", "tier": 1, "count": 4},   
        ],
        "reward": 48,
        "spawn_rate": 54,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 3, "count": 6},
            {"type": "square",   "tier": 3, "count": 4},
            {"type": "star",     "tier": 2, "count": 4},
            {"type": "triangle", "tier": 1, "count": 4},   
            {"type": "boss",     "tier": 2, "count": 1},
        ],
        "reward": 58,
        "spawn_rate": 52,
    },

    # ────────────────────────── 11-15 : tier-3/4 finale ─────────────────────
    {
        "steps": [
            {"type": "triangle", "tier": 3, "count": 8},
            {"type": "square",   "tier": 3, "count": 6},
            {"type": "star",     "tier": 3, "count": 4},
            {"type": "triangle", "tier": 2, "count": 6},   
        ],
        "reward": 72,
        "spawn_rate": 48,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 6},
            {"type": "square",   "tier": 3, "count": 8},
            {"type": "star",     "tier": 3, "count": 8},
            {"type": "square",   "tier": 1, "count": 6},   
        ],
        "reward": 85,
        "spawn_rate": 46,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 6},
            {"type": "square",   "tier": 4, "count": 6},
            {"type": "star",     "tier": 3, "count": 8},
            {"type": "triangle", "tier": 2, "count": 6},   
            {"type": "boss",     "tier": 3, "count": 1},
        ],
        "reward": 100,
        "spawn_rate": 44,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 8},
            {"type": "square",   "tier": 4, "count": 8},
            {"type": "star",     "tier": 4, "count": 6},
            {"type": "square",   "tier": 2, "count": 8},   
        ],
        "reward": 120,
        "spawn_rate": 42,
    },
    {
        "steps": [
            {"type": "triangle", "tier": 4, "count": 10},
            {"type": "square",   "tier": 4, "count": 10},
            {"type": "star",     "tier": 4, "count": 10},
            {"type": "triangle", "tier": 2, "count": 8},   
            {"type": "boss",     "tier": 4, "count": 1},
        ],
        "reward": 150,
        "spawn_rate": 38,
    },
]
