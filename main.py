"""Start AiiDA REST API for default profile."""
import os

from aiida.restapi import api
from aiida.restapi.run_api import run_api
from aiida.manage.configuration import load_profile, load_config
from aiida.manage.configuration.profile import Profile
import aiida.restapi

config = load_config(create=True)

profile_name = os.getenv("AIIDA_PROFILE")

profile = Profile(profile_name, {
    "database_hostname": os.getenv("AIIDADB_HOST"),
    "database_port": os.getenv("AIIDADB_PORT"),
    "database_engine": os.getenv("AIIDADB_ENGINE"),
    "database_name": os.getenv("AIIDADB_NAME"),
    "database_username": os.getenv("AIIDADB_USER"),
    "database_password": os.getenv("AIIDADB_PASS"),
    "database_backend": os.getenv("AIIDADB_BACKEND"),
    "default_user": os.getenv("default_user_email"),
    "repository_uri": "file://{}/.aiida/repository/{}".format(os.getenv("AIIDA_PATH"), profile_name),
})
config.add_profile(profile)
config.set_default_profile(profile_name)
config.store()

load_profile(profile_name)

CONFIG_DIR = os.path.join(os.path.split(os.path.abspath(aiida.restapi.__file__))[0], 'common')

(app, api) = run_api(api.App,
                             api.AiidaApi,
                             hostname="localhost",
                             port=5000,
                             config=CONFIG_DIR,
                             debug=False,
                             wsgi_profile=False,
                             hookup=False,
                             catch_internal_server=False)
