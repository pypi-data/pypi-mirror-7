from hatak.application import Application

from .routes import make_routes

main = Application('{{settings["package:name"]}}', make_routes)
