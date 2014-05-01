import os


def lua_scripts():
    """
    Load up lua scripts
    """
    script_dict = {
        "articlestore_save_articles": None,
    }

    curdir = os.path.dirname(os.path.abspath(__file__))

    for script_name in script_dict.keys():
        script = None
        with open(os.path.join(curdir, "{0}.lua".format(script_name)), "r") as f:
            script = f.read()

        script_dict[script_name] = script

    return script_dict
