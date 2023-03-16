from configparser import ConfigParser


def config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)

    if not parser.has_section(section):
        raise Exception(f"Section {section} not found in the {filename} file")

    db = {param[0]: param[1] for param in parser.items(section)}

    return db
