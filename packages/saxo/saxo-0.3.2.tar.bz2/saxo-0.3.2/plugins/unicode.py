# http://inamidst.com/saxo/
# Created by Sean B. Palmer

import os.path
import saxo
import unicodedata

surrogates = {"D800", "DB7F", "DB80", "DBFF", "DC00", "DFFF"}

def create_table(db):
    db["saxo_unicode"].create(
        ("hexcode", str),
        ("codepoint", int),
        ("name", str),
        ("current", str),
        ("ancient", str),
        ("category", str),
        ("character", str),
        ("display", str))

def populate_table_python(db):
    for codepoint in range(1, 0x10000):
        hexcode = "%04X" % codepoint

        # Skip surrogates
        if hexcode in surrogates:
            character = ""
        else:
            character = chr(codepoint)

        try: category = unicodedata.category(character)
        except TypeError:
            continue

        try: character.encode("utf-8")
        except UnicodeEncodeError:
            continue

        if category.startswith("M"):
            # TODO: Just Mn?
            display = "\u25CC" + character
        elif category.startswith("C") and not category.endswith("o"):
            # Co is Private_Use, allow those
            if 0 <= codepoint <= 0x1F:
                display = chr(codepoint + 0x2400)
            else:
                display = "<%s>" % category
        else:
            display = character

        try: name = unicodedata.name(character)
        except ValueError:
            name = "<control>"

        current = name[:]
        ancient = ""

        db["saxo_unicode"].insert((hexcode, codepoint, name, current,
            ancient, category, character, display), commit=False)

    db.commit()

@saxo.setup
def setup(irc):
    path = os.path.join(irc.base, "database.sqlite3")
    with saxo.database(path) as db:
        if "saxo_unicode" not in db:
            create_table(db)
            populate_table_python(db)
