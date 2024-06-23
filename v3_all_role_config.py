ALL_ROLE_CONFIG_LIST = [
    {
        "role_name": "modao",
        "role_status": "todo",
        "role_xy": [3 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["up", "right", "space"], "back_swing": 0.3},
            {"key_list": ["up", "up", "space"], "back_swing": 0.3},
            {"key_list": ["down", "up", "space"], "back_swing": 0.3},
            {"key_list": ["down", "space"], "back_swing": 0.3},
            {"key_list": ["space"], "back_swing": 0.3}
        ],
        "handle_monster": [
            {"key_list": ["w"], "back_swing": 0.3}
        ],
        "handle_boss": [
            {"key_list": ["w"], "back_swing": 0.3}
        ]
    },
    {
        "role_name": "naima01",
        "role_status": "todo",
        "role_xy": [4 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.3},
            {"key_list": ["up", "up", "space"], "back_swing": 0.3},
            {"key_list": ["down", "left", "space"], "back_swing": 0.3},
            {"key_list": ["e"], "back_swing": 0.3}
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
        "role_xy": [5 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.3},
            {"key_list": ["up", "up", "space"], "back_swing": 0.5},
            {"key_list": ["f"], "back_swing": 0.3}
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
        "role_xy": [6 / 8, 1 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.3},
            {"key_list": ["up", "up", "space"], "back_swing": 0.3},
            {"key_list": ["down", "left", "space"], "back_swing": 0.3},
            {"key_list": ["e"], "back_swing": 0.3}
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
        "role_xy": [7 / 8, 1 / 3],
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
            {"key_list": ["right", "right", "space"], "back_swing": 0.3},
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
            {"key_list": ["right", "right", "space"], "back_swing": 0.3},
            {"key_list": ["r"], "back_swing": 0.3}
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
        "role_xy": [2 / 8, 2 / 3],
        "handle_buff": [
            {"key_list": ["right", "right", "space"], "back_swing": 0.3},
            {"key_list": ["r"], "back_swing": 0.3}
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
SKILL_BOX_Y2 = 713
SKILL_BOX_X_OFFSET = 31
SKILL_BOX_Y_OFFSET = 31
SKILL_BOX_WIDTH = 30
SKILL_BOX_HEIGHT = 30
SKILL_ICON_LOCATION = {
    "q": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (1 - 1), SKILL_BOX_Y1],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (1 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "w": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (2 - 1), SKILL_BOX_Y1],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (2 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "e": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (3 - 1), SKILL_BOX_Y1],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (3 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "r": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (4 - 1), SKILL_BOX_Y1],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (4 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "t": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (5 - 1), SKILL_BOX_Y1],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (5 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "y": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (6 - 1), SKILL_BOX_Y1],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (6 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "ctrl": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (7 - 1), SKILL_BOX_Y1],
             [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (7 - 1) + SKILL_BOX_WIDTH, SKILL_BOX_Y1 + SKILL_BOX_HEIGHT]],
    "a": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (1 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (1 - 1) + SKILL_BOX_WIDTH,
           SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
    "s": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (2 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (2 - 1) + SKILL_BOX_WIDTH,
           SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
    "d": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (3 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (3 - 1) + SKILL_BOX_WIDTH,
           SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
    "f": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (4 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (4 - 1) + SKILL_BOX_WIDTH,
           SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
    "g": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (5 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (5 - 1) + SKILL_BOX_WIDTH,
           SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
    "h": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (6 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
          [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (6 - 1) + SKILL_BOX_WIDTH,
           SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
    "alt": [[SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (7 - 1), SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET],
            [SKILL_BOX_X1 + SKILL_BOX_X_OFFSET * (7 - 1) + SKILL_BOX_WIDTH,
             SKILL_BOX_Y1 + SKILL_BOX_Y_OFFSET + SKILL_BOX_HEIGHT]],
}

if __name__ == '__main__':
    print(SKILL_ICON_LOCATION)
