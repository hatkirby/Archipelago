exits_by_region = {
    "Menu": {
        "New Game": [
            ["Menu", "Blank start", []]
        ]
    },
    "Apartment floor 1": {
        "Apartment floor 1 to Suburb exit": [
            ["Apartment floor 1", "Suburb", []],
            ["Suburb", "Apartment floor 1", []]
        ],
        "Apartment floor 1 to Apartment floor 2": [
            ["Apartment floor 1", "Apartment floor 2", []],
            ["Apartment floor 2", "Apartment floor 1", []]
        ]
    },
    "Apartment floor 2": {
        "Apartment floor 2 to Apartment floor 3": [
            ["Apartment floor 2", "Apartment floor 3", []],
            ["Apartment floor 3", "Apartment floor 2", []]
        ]
    },
    "Beach": {
        "Beach to Fields exit": [
            ["Beach", "Fields", []],
            ["Fields", "Beach", []]
        ],
        "Beach to Red Sea exit": [
            ["Beach", "Red Sea", ["Any Broom but swapper"]],
            ["Red Sea", "Beach", []]
        ]
    },
    "Bedroom": {
        "Bedroom to Overworld exit": [
            ["Bedroom", "Overworld", []],
            ["Overworld", "Bedroom", []]
        ],
        "Bedroom to Overworld post windmill exit": [
            ["Bedroom", "Overworld post windmill", ["Windmill activated"]],
            ["Overworld post windmill", "Bedroom", ["Windmill activated"]]
        ]
    },
    "Bedroom drawer": {
        "Bedroom drawer to Drawer exit": [
            ["Bedroom drawer", "Drawer", ["Swap upgrade", "Swap unlocked"]],
            ["Drawer", "Bedroom drawer", ["Swap upgrade", "Swap unlocked"]]
        ],
        "Bedroom drawer to Overworld exit": [
             ["Bedroom drawer", "Overworld", ["Swap upgrade", "Swap unlocked"]],
             ["Overworld", "Bedroom drawer", ["Swap upgrade", "Swap unlocked"]]
         ]
    },
    "Blank start": {
        "Blank start to Nexus exit": [
            ["Blank start", "Nexus bottom", []],
        ]
    },
    "Blank windmill": {
        "Blank windmill to Windmill exit": [
            ["Blank windmill", "Windmill", ["Swap upgrade", "Swap unlocked"]],
            ["Windmill", "Blank windmill", ["Swap upgrade", "Swap unlocked"]]
        ],
        "Blank windmill to Drawer dark exit": [
            ["Blank windmill", "Drawer dark", ["Cards:47"]],
            ["Drawer dark", "Blank windmill", ["Cards:47"]]
        ]
    },
    "Blue": {
        "Blue to Go top exit": [
            ["Blue", "Go top", []],
            ["Go top", "Blue", []]
        ]
    },
    "Cell": {
        "Cell to Circus exit": [
            ["Cell", "Circus", []],
            ["Circus", "Cell", []]
        ],
        "Cell to Red Cave top exit": [
            ["Cell", "Red Cave top", ["Windmill activated"]],
            ["Red Cave top", "Cell", ["Windmill activated"]]
        ],
    },
    "Cliff": {
        "Cliff to Forest exit": [
            ["Cliff", "Forest", []],
            ["Forest", "Cliff", []]
        ],
        "Cliff to Crowd floor 2 exit": [
            ["Cliff", "Crowd floor 2", []],
            ["Crowd floor 2", "Cliff", []]
        ],
        "Cliff to Crowd jump challenge exit": [
            ["Cliff", "Crowd jump challenge", []],
            ["Crowd jump challenge", "Cliff", []]
        ]
    },
    "Cliff post windmill": {
        "Cliff post windmill to Space exit": [
            ["Cliff post windmill", "Space", []],
            ["Space", "Cliff post windmill", []]
        ],
        "Cliff post windmill to Crowd exit": [
            ["Crowd floor 1", "Cliff post windmill", ["Windmill activated"]],
            ["Cliff post windmill", "Crowd floor 1", ["Windmill activated"]]
        ]
    },
    "Crowd floor 2": {
        "Crowd floor 2 to Crowd floor 1 exit": [
            ["Crowd floor 2", "Crowd floor 1", []],
            ["Crowd floor 1", "Crowd floor 2", []]
        ],
        "Crowd floor 2 to Crowd floor 3 exit": [
            ["Crowd floor 2", "Crowd floor 3", []],
            ["Crowd floor 3", "Crowd floor 2", []]
        ]
    },
    "Debug": {
        "Debug to Nexus top exit": [
            ["Debug", "Nexus top", []],
            ["Nexus top", "Debug", []]
        ]
    },
    "Drawer dark": {
        "Drawer dark to Nexus top exit": [
             ["Drawer dark", "Nexus top", []],
             ["Nexus top", "Drawer dark", []]
         ]
    },
    "Fields": {
        "Fields to Overworld exit": [
            ["Fields", "Overworld", ["Green key"]],
            ["Overworld", "Fields", ["Green key"]]
        ],
        "Fields to Forest exit": [
            ["Fields", "Forest", ["Goldman moved"]],
            ["Forest", "Fields", []]
         ],
        "Fields to Terminal exit": [
             ["Fields", "Terminal", ["Red key", "Jump shoes"]],
             ["Terminal", "Fields", ["Red key", "Jump shoes"]]
         ],
        "Fields to Windmill exit": [
             ["Fields", "Windmill", ["Green key", "Red key", "Blue key"]],
             ["Windmill", "Fields", ["Green key", "Red key", "Blue key"]]
         ]
    },
    "Go bottom": {
        "Go bottom to Terminal exit": [
             ["Go bottom", "Terminal", ["Cards:36"]],
             ["Terminal", "Go bottom", ["Cards:36"]]
         ],
        "Go bottom to Go top exit": [
             ["Go bottom", "Go top", ["Swap upgrade"]],
             ["Go top", "Go bottom", ["Swap upgrade"]]
         ]
    },
    "Go top": {
        "Go top to Happy exit": [
             ["Go top", "Happy", ["Blue completed"]],
             ["Happy", "Go top", ["Blue completed"]]
         ]
    },
    "Hotel roof": {
        "Hotel roof to Space exit": [
             ["Hotel roof", "Space", []],
             ["Space", "Hotel roof", []]
         ],
        "Hotel roof to Hotel floor 4": [
            ["Hotel roof", "Hotel floor 4", []],
            ["Hotel floor 4", "Hotel roof", []]
        ]
    },
    "Hotel floor 4": {
        "Hotel floor 4 to Hotel floor 3": [
            ["Hotel floor 4", "Hotel floor 3", []],
            ["Hotel floor 3", "Hotel floor 4", []]
        ]
    },
    "Hotel floor 3": {
        "Hotel floor 3 to Hotel floor 2": [
            ["Hotel floor 3", "Hotel floor 2", []],
            ["Hotel floor 2", "Hotel floor 3", []]
        ]
    },
    "Hotel floor 2": {
        "Hotel floor 2 to Hotel floor 1": [
            ["Hotel floor 2", "Hotel floor 1", []],
            ["Hotel floor 1", "Hotel floor 2", []]
        ]
    },
    "Nexus bottom": {
        "Nexus bottom to Street exit": [
            ["Nexus bottom", "Street", []],
            ["Street", "Nexus bottom", []]
        ],
    },
    "Nexus top": {
        "Nexus top to Boss Rush exit": [
             ["Nexus top", "Boss Rush", []],
             ["Boss Rush", "Nexus top", []]
         ],
        "Nexus top to Blank ending exit": [
             ["Nexus top", "Blank ending", ["Cards:49"]],
             ["Blank ending", "Nexus top", ["Cards:49"]]
         ]
    },
    "Overworld post windmill": {
        "Overworld post windmill to Suburb ending exit": [
             ["Overworld post windmill", "Suburb", []],
             ["Suburb", "Overworld post windmill", []]
         ],
        "Overworld post windmill to Overworld exit": [
             ["Overworld post windmill", "Overworld", []]
         ]
    },
    "Red Cave center": {
        "Red Cave center to Red Sea exit": [
             ["Red Cave center", "Red Sea", []],
             ["Red Sea", "Red Cave center", []]
         ]
    },
    "Red Cave left": {
        "Red Cave left to Red Sea exit": [
             ["Red Cave left", "Red Sea", []],
             ["Red Sea", "Red Cave left", ["Center left tentacle hit"]]
         ]
    },
    "Red Cave right": {
        "Red Cave right to Red Sea exit": [
             ["Red Cave right", "Red Sea", []],
             ["Red Sea", "Red Cave right", ["Center right tentacle hit"]]
         ]
    },
    "Red Cave top": {
        "Red Cave top to Red Sea exit": [
             ["Red Cave top", "Red Sea", []],
             ["Red Sea", "Red Cave top", ["Left tentacle hit", "Right tentacle hit"]]
         ]
    },
    "Red Cave bottom": {
        "Red Cave bottom to Red Sea exit": [
             ["Red Cave bottom", "Red Sea", []],
             ["Red Sea", "Red Cave bottom", []]
         ]
    },
    "Red Cave Isaac": {
        "Red Cave Isaac to Red Sea exit": [
             ["Red Cave Isaac", "Red Sea", []],
             ["Red Sea", "Red Cave Isaac", []]
         ]
    },
    "Street": {
        "Street to Overworld exit": [
             ["Street", "Overworld", ["Keys:1"]],
         ]
    }
}
