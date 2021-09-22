import os

import pandas as pd
from jinja2 import Template


def clean_name(s):
    s = s.strip()
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


def clean_entry(entry):
    v = entry.values[0]
    if pd.isna(v):
        return ""
    else:
        return v.rstrip().replace("\n", "<br/>")


def get_photos(name_raw):
    # Check for many speakers
    names = name_raw.split(",")
    photos = []
    for speaker_name in names:
        speaker_photo = f"../images/speakers/{clean_name(speaker_name)}.jpg"

        if os.path.isfile(speaker_photo):
            print("Speaker photo found:", speaker_photo)
            # We remove the relativeness from the path that we
            # know it starts with "../"
            photos.append(speaker_photo[3:])
        else:
            print(f"No speaker photo for {speaker_name}: {speaker_photo}")
            photos.append(default_photo)
    return " ".join(photos)


def get_dict(day):
    """
    Build a dictionary based on the information from different
    CSV files, to populate the schedule from the website.
    """
    d = {}
    i = 0

    for _, row in agenda.iterrows():
        name = photo = url = title = desc = social = bio = None
        row_day = row["day"]

        start = row["start"]
        end = row["end"]

        talk_a = row["talk_a"].strip()
        talk_b = row["talk_b"].strip()

        for bloque, title in enumerate([talk_a, talk_b]):

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
                desc = (
                    "El sábado 2 de octubre de 2021 a las 18:30 en primera "
                    "convocatoria y a las 19:00 en segunda convocatoria "
                    "(hora peninsular) se celebrará la Asamblea "
                    "Extraordinaria de la Asociación. Como viene siendo "
                    "habitual, la asamblea extraordinaria se celebrará al "
                    "finalizar la primera jornada de la PyConES 2021.<br/>"
                    "Para el comienzo y amenizar la espera entre la primera "
                    "y segunda convocatoria, prepararemos alguna sorpresa "
                    "y puede que hasta podáis ganar algún premio. Así que "
                    "¡sed puntuales!"
                )

            # TODO: Agregar más información
            elif title == "Almuerzo":
                name = ""
                url = ""
                desc = ""
                photo = default_photo
            elif title.startswith("Keynote"):
                found = keynotes.loc[keynotes["title"].str.strip() == title]
                name = found["name"].values[0]
                url = found["url"].values[0]
                social = found["social"].values[0]
                bio = found["bio"].values[0]
                photo = found["photo"].values[0]
            elif title.startswith("Taller"):
                found = talleres.loc[
                    talleres["title"].str.strip() == title.replace("Taller: ", "")
                ]
                name = clean_entry(found["author"])
                url = clean_entry(found["url"])
                social = clean_entry(found["social"])
                desc = clean_entry(found["description"])
                bio = clean_entry(found["bio"])
                photo = get_photos(name)
            # TODO: Agregar más información
            elif title.startswith("Sponsor"):
                # Hack to avoid empty sponsors
                # TBD: To be determined
                if 'TBD' in title:
                    continue
                found = sponsors.loc[
                    sponsors["title"].str.strip() == title.replace("Sponsor: ", "")
                ]
                name = found["name"].values[0]
                url = found["url"].values[0]
                social = found["social"].values[0]
                desc = found["description"].values[0]
                photo = found["photo"].values[0]
            else:
                found = charlas.loc[charlas["title"].str.strip() == title]
                name = clean_entry(found["name"])
                url = clean_entry(found["url"])
                social = clean_entry(found["social"])
                bio = clean_entry(found["bio"])
                desc = clean_entry(found["description"])
                # We use relative, because the 'images' directory is not here.

                photo = get_photos(name)

            # Add to the returning dict
            if row_day == day:
                # start end name photo url title description block social
                d[i] = [
                    start,
                    end,
                    name,
                    photo,
                    url,
                    title,
                    desc,
                    bio,
                    ("A", "B")[bloque],
                    social,
                ]
                i += 1

    return d


if __name__ == "__main__":

    charlas = pd.read_csv("charlas.csv", sep=";")
    talleres = pd.read_csv("talleres.csv")
    agenda = pd.read_csv("agenda.csv", sep=";")
    keynotes = pd.read_csv("keynotes.csv", sep=";")
    sponsors = pd.read_csv("sponsors.csv", sep=";")
    print(talleres)
    print(charlas)
    print(agenda)
    print(keynotes)
    print(sponsors)
    default_photo = "images/resource/thumb-1.jpg"
    columnas = (
        "start",
        "end",
        "name",
        "photo",
        "url",
        "title",
        "description",
        "bio",
        "block",
        "social",
    )

    conf = {
        day: pd.DataFrame.from_dict(get_dict(day), orient="index", columns=columnas)
        for day in ("sabado", "domingo")
    }
    rendered_template = Template(open("base.html").read()).render(conf)

    # Write final HTML
    with open("../index.html", "w") as f:
        f.write(rendered_template)
        print("Written file ../index.html")
