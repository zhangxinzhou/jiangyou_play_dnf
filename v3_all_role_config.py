ALL_ROLE_CONFIG_LIST = [
    {
        "role_name": "modao",
        "role_status": "todo",
        "role_xy": [2 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["up", "right", "space"], "back_swing": 0.5},
            {"key_list": ["up", "up", "space"], "back_swing": 2},
            {"key_list": ["down", "space"], "back_swing": 0.5},
            {"key_list": ["space"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["s"], "back_swing": 0.5},
            {"key_list": ["f"], "back_swing": 0.5, "duration": 0.5},
            {"key_list": ["r"], "back_swing": 0.5},
            {"key_list": ["t"], "back_swing": 0.5}
        ],
        "handle_boss": [
            {"key_list": ["q"], "back_swing": 3}
        ]
    },
    {
        "role_name": "naima01",
        "role_status": "todo",
        "role_xy": [3 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.5},
            {"key_list": ["up", "up", "space"], "back_swing": 0.5},
            {"key_list": ["down", "left", "space"], "back_swing": 0.5},
            {"key_list": ["e"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["s"], "back_swing": 1}
        ],
        "handle_boss": [
            {"key_list": ["q", "a"], "back_swing": 2}
        ]
    },
    {
        "role_name": "nailuo",
        "role_status": "todo",
        "role_xy": [4 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 2},
            {"key_list": ["up", "up", "space"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["f"], "back_swing": 0.8}
        ],
        "handle_boss": [
            {"key_list": ["a"], "back_swing": 1},
            {"key_list": ["h"], "back_swing": 1}
        ]
    },
    {
        "role_name": "naima02",
        "role_status": "todo",
        "role_xy": [5 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.5},
            {"key_list": ["up", "up", "space"], "back_swing": 0.5},
            {"key_list": ["down", "left", "space"], "back_swing": 0.5},
            {"key_list": ["e"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["s"], "back_swing": 1}
        ],
        "handle_boss": [
            {"key_list": ["q", "a"], "back_swing": 2}
        ]
    },
    {
        "role_name": "zhaohuan",
        "role_status": "todo",
        "role_xy": [6 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["q"], "back_swing": 2},
            {"key_list": ["r"], "back_swing": 0.5},
            {"key_list": ["t"], "back_swing": 0.5},
            {"key_list": ["up", "right", "up", "space"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["r"], "back_swing": 1}
        ],
        "handle_boss": [
            {"key_list": ["y"], "back_swing": 2}
        ]
    },
    {
        "role_name": "saber",
        "role_status": "todo",
        "role_xy": [1 / 8, 2 / 3],
        "handle_buff": [
            {"key_list": ["q", "left"], "back_swing": 0.1},
            {"key_list": ["right", "right", "space"], "back_swing": 0.5},
            {"key_list": ["a"], "duration": 2, "back_swing": 0.1}
        ],
        "handle_monster": [
            {"key_list": ["s"], "duration": 0.8, "back_swing": 1}
        ],
        "handle_boss": [
            {"key_list": ["up", "up", "down", "down", "z"], "back_swing": 2}
        ]
    },
    {
        "role_name": "zhanfa",
        "role_status": "todo",
        "role_xy": [2 / 8, 2 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.5},
            {"key_list": ["r"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["e"], "back_swing": 1}
        ],
        "handle_boss": [
            {"key_list": ["t"], "back_swing": 3}
        ]
    },
    {
        "role_name": "papading",
        "role_status": "todo",
        "role_xy": [3 / 8, 2 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.5},
            {"key_list": ["r"], "back_swing": 0.5}
        ],
        "handle_monster": [
            {"key_list": ["e"], "back_swing": 1}
        ],
        "handle_boss": [
            {"key_list": ["t"], "back_swing": 3}
        ]
    }
]

SKILL_BOX_X1 = 538
SKILL_BOX_Y1 = 652
SKILL_BOX_X2 = 756
SKILL_BOX_Y2 = 714
SKILL_BOX_X_OFFSET = 31
SKILL_BOX_Y_OFFSET = 31
SKILL_BOX_WIDTH = 28
SKILL_BOX_HEIGHT = 28
X1 = SKILL_BOX_X1 + 2
Y1 = SKILL_BOX_Y1 + 2
WIDTH = SKILL_BOX_WIDTH
HEIGHT = SKILL_BOX_HEIGHT
X_OFFSET = SKILL_BOX_X_OFFSET
Y_OFFSET = SKILL_BOX_Y_OFFSET
SKILL_ICON_LOCATION = {
    "q": [X1 + X_OFFSET * (1 - 1), Y1, X1 + X_OFFSET * (1 - 1) + WIDTH, Y1 + HEIGHT],
    "w": [X1 + X_OFFSET * (2 - 1), Y1, X1 + X_OFFSET * (2 - 1) + WIDTH, Y1 + HEIGHT],
    "e": [X1 + X_OFFSET * (3 - 1), Y1, X1 + X_OFFSET * (3 - 1) + WIDTH, Y1 + HEIGHT],
    "r": [X1 + X_OFFSET * (4 - 1), Y1, X1 + X_OFFSET * (4 - 1) + WIDTH, Y1 + HEIGHT],
    "t": [X1 + X_OFFSET * (5 - 1), Y1, X1 + X_OFFSET * (5 - 1) + WIDTH, Y1 + HEIGHT],
    "y": [X1 + X_OFFSET * (6 - 1), Y1, X1 + X_OFFSET * (6 - 1) + WIDTH, Y1 + HEIGHT],
    "ctrl": [X1 + X_OFFSET * (7 - 1), Y1, X1 + X_OFFSET * (7 - 1) + WIDTH, Y1 + HEIGHT],

    "a": [X1 + X_OFFSET * (1 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (1 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
    "s": [X1 + X_OFFSET * (2 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (2 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
    "d": [X1 + X_OFFSET * (3 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (3 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
    "f": [X1 + X_OFFSET * (4 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (4 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
    "g": [X1 + X_OFFSET * (5 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (5 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
    "h": [X1 + X_OFFSET * (6 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (6 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
    "alt": [X1 + X_OFFSET * (7 - 1), Y1 + Y_OFFSET, X1 + X_OFFSET * (7 - 1) + WIDTH, Y1 + Y_OFFSET + HEIGHT],
}

if __name__ == '__main__':
    print(SKILL_ICON_LOCATION)
