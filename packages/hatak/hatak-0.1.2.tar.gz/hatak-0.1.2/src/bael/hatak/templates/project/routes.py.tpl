from hatak.route import Route


def make_routes(app):
    route = Route(app, '{{settings["package:name"]}}.')
