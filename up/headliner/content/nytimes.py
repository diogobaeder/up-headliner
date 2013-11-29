SECTIONS = ["arts", "automobiles", "business", "dining", "education", "fashion", "garden", "health", "movies", "music", "politics", "science", "sports", "style", "technology", "television", "travel", "your-money"]

MAPPING = {
        "arts": {
            "__PATH": {
                "video-games" : ["Video-Games"],
                "design" : ["Design"],
                "__NONE": ["Arts"],
            },
        },

        "automobiles": {
            "__ALL": ["Autos"],
        },

        "business": {
            "__ALL": ["Business"],
            "__PATH": {
                "smallbusiness": ["Entrepreneur"],
            },
        },

        "dining": {
            "__ALL": ["Cooking"],
        },

        "education": {
            "__ALL": ["Ideas"],
        },

        "fashion": {
            "__ALL": ["Fashion-Men", "Fashion-Women"],
            "__PATH": {
                "weddings": ["Weddings"],
            }
        },

        "garden": {
            "__ALL": ["Do-It-Yourself", "Home-Design"],
        },

        "health": {
            "__ALL": ["Health-Men", "Health-Women"],
        },

        "movies": {
            "__ALL": ["Movies"],
        },

        "music": {
            "__ALL": ["Music"],
        },

        "politics": {
            "__ALL": ["Politics"],
        },


        "science": {
            "__ALL": ["Science"],
        },

        "sports": {
            "__ALL": ["Sports"],
            "__PATH": {
                "baseball": ["Baseball"],
                "basketball": ["Basketball"],
                "football": ["Football"],
                "golf": ["Golf"],
                "hockey": ["Hockey"],
                "soccer": ["Soccer"],
                "tennis": ["Tennis"],
            },
            "__KEYWORD": {
                "boxing": ["Boxing"],
            },
            "__COLUMN": {
                "On Boxing": ["Boxing"],
            },
        },

        "style": {
            "__KEYWORD": {
                "parenting": ["Parenting"]
            },
            "__FACET": {
                "parenting": ["Parenting"]
            }
        },

        "technology": {
            "__ALL" : ["Programming", "Technology"],
            "__PATH": {
                "personaltech": ["Android", "Apple"],
            },
        },

        "television": {
            "__ALL" : ["Television"],
        },

        "travel": {
            "__ALL" : ["Travel"],
        },

        "your-money": {
                "_ALL": ["Business"],
        }
}
