import json
import os

import connexion
from flask import redirect


class Factory:

    def __init__(self, app=None, config=None, config_env=(os.getenv('SHORTLY_ENV', 'production'))):
        self.app = app
        self.config = config
        self.config_env = config_env

    @staticmethod
    def get_module_directory() -> str:
        """ Return module directory """
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    @staticmethod
    def get_config_directory() -> str:
        """ Return configuration directory """
        return os.path.join(Factory.get_module_directory(), 'config')

    def load_configuration(self) -> None:
        try:
            config_file = os.path.join(self.get_config_directory(), self.config_env + '.json')
            with open(config_file) as data_file:
                self.config = json.load(data_file)
        except FileNotFoundError:
            config_file = os.path.join(self.get_config_directory(), 'skeleton', self.config_env + '.json')
            with open(config_file) as data_file:
                self.config = json.load(data_file)

    def update_flask_configuration(self) -> None:
        """ Load flask configuration """
        self.app.app.config.update(self.config['FLASK'])

    def init_connexion_app(self):
        """ Create Connexion app and define custom ettings """
        swagger_path = os.path.join(Factory.get_module_directory(), 'static', 'swagger-ui')
        spec_dir = os.path.join(Factory.get_module_directory(), 'swagger')
        if os.path.exists(swagger_path):
            self.app = connexion.App(__name__, specification_dir=spec_dir, options={"swagger_path": swagger_path})
        else:
            self.app = connexion.App(__name__, specification_dir=spec_dir)

    def setup_flask(self):
        """ Setup flask"""
        self.setup_flask_routes()

    def setup_flask_routes(self):
        """ Define default flask routes """
        @self.app.app.route('/')
        def site_root():
            """ Redirect Root URL to Swagger UI """
            return redirect(self.config['SERVICES'][0]['base_path'] + 'ui/')

    def setup_connexion_routes(self):
        for service in self.config['SERVICES']:
            self.app.add_api(service['file'],
                             base_path=service['base_path'],
                             validate_responses=service['validate_responses'])

    @property
    def get_routes(self):
        return self.app.app.url_map

    def init(self):
        self.init_connexion_app()
        self.load_configuration()
        self.setup_connexion_routes()
        self.update_flask_configuration()
        self.setup_flask()

    def run_server(self):
        """ run flask server """
        self.app.run(host=self.config['FLASK']['HOST'],
                     port=self.config['FLASK']['PORT'],
                     debug=self.config['FLASK']['DEBUG'])
