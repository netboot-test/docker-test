from beapi import factory
from flask_script import Manager

""" Store factory instance """
flask_app = factory.app.app
manager = Manager(flask_app)


@manager.command
def routes():
    """ Show all routes available """
    return factory.get_routes


@manager.command
def run():
    """ Run App """
    factory.run_server()


@manager.command
def config():
    """ Dumps config """
    return flask_app.config


if __name__ == '__main__':
    manager.run()
