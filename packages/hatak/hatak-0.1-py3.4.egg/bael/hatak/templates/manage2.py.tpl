#!/usr/bin/env python
from migrate.versioning.shell import main
from {{settings["package:name"]}}.application.init import Application


def get_settings():
    settings, paths = Application.get_settings('{{settings["package:name"]}}')
    merged = settings.merged(paths)
    return merged.to_dict()

if __name__ == '__main__':
    settings = get_settings()
    main(url=settings['db:url'], debug='False', repository='migrations')
