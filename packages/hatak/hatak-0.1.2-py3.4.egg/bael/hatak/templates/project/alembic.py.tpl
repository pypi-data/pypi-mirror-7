from hatak.alembic import AlembicStarter


def run():
    AlembicStarter('{{settings["package:name"]}}')()
