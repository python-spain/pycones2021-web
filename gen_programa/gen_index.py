import os
import pandas as pd
from jinja2 import Template


def clean(s):
    r = (
        ("_", ""),
        (".", ""),
        (" ", "_"),
        (",", "_"),
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ç", "c"),
        ("ñ", "n"),
        ("-", "_"),
        ("|", "_"),
    )
    for before, after in r:
        s = s.replace(before, after)
    return s.lower()


def get_dict(day):
    """
    Build a dictionary based on the information from different
    CSV files, to populate the schedule from the website.
    """
    d = {}
    i = 0

    for _, row in agenda.iterrows():
        name = photo = url = title = description = twitter = bio = None
        row_day = row["day"]

        start = row["start"]
        end = row["end"]

        talk_a = row["talk_a"].strip()
        talk_b = row["talk_b"].strip()

        for bloque, title in enumerate([talk_a, talk_b]):
            # default empty photo
            photo = "images/resource/thumb-1.jpg"

            if title == "Apertura de la jornada":
                name = "Organización PyConES"
                url = "https://es.python.org"
                desc = "Transmisión inicial"
                photo = "images/pythonES_logo_simple.png"
            elif title == "Sorteos y Clausura":
                name = "Organización PyConES"
                url = "https://es.python.org"
                desc = "Transmisión final"
                photo = "images/pythonES_logo_simple.png"
            elif title == "Asamblea Extraordinaria de Python España":
                name = "Directiva Python España"
                url = "https://es.python.org"
                photo = "images/pythonES_logo_simple.png"
                desc = ""
            # TODO: Agregar más información
            elif title == "Almuerzo":
                name = ""
                url = ""
                desc = ""
            elif title.startswith("Keynote"):
                found = keynotes.loc[keynotes["title"].str.strip() == title]
                name = found["name"].values[0]
                url = found["url"].values[0]
                twitter = found["twitter"].values[0]
                # TODO: Pendiente
                # desc = found["description"].values[0]
                photo = found["photo"].values[0]
            elif title.startswith("Taller"):
                found = talleres.loc[talleres["title"].str.strip() == title.replace("Taller: ", "")]
                name = clean_entry(found["author"])
                url = clean_entry(found["url"])
                desc = clean_entry(found["description"])
                bio = clean_entry(found["bio"])
            # TODO: Agregar más información
            elif title.startswith("Sponsor"):
                name = ""
                url = ""
                desc = ""

            else:
                found = charlas.loc[charlas["title"].str.strip() == title]
                name = clean_entry(found["name"])
                url = clean_entry(found["url"])
                twitter = clean_entry(found["twitter"])
                bio = clean_entry(found["bio"])
                desc = clean_entry(found["description"])
                # We use relative, because the 'images' directory is not here.
                speaker_photo = f"../images/{clean(name)}.jpg"
                if os.path.isfile(speaker_photo):
                    print("Speaker photo found:", speaker_photo)
                    # We remove the relativeness from the path that we
                    # know it starts with "../"
                    photo = speaker_photo[3:]
                else:
                    print(f"No speaker photo for {name}: {speaker_photo}")

            if row_day == day:
                # start end name photo url title description block twitter
                d[i] = [start, end, name, photo, url, title, desc, bio, ("A", "B")[bloque], twitter]
                i += 1

    return d

def clean_entry(entry):
    v = entry.values[0]
    if pd.isna(v):
        return ""
    else:
        return v.rstrip().replace("\n", "<br/>")


if __name__ == "__main__":

    charlas = pd.read_csv("charlas.csv", sep=";")
    talleres = pd.read_csv("talleres.csv")
    agenda = pd.read_csv("agenda.csv", sep=";")
    keynotes = pd.read_csv("keynotes.csv", sep=";")
    print(talleres)
    print(charlas)
    print(agenda)
    print(keynotes)
    columnas = ("start", "end", "name", "photo", "url", "title", "description", "bio", "block", "twitter")

    conf = {
        day: pd.DataFrame.from_dict(get_dict(day), orient="index", columns=columnas)
        for day in ("sabado", "domingo")
    }
    rendered_template = Template(open("base.html").read()).render(conf)

    # Write final HTML
    with open(f"../index.html", "w") as f:
        f.write(rendered_template)
        print("Written file ../index.html")
