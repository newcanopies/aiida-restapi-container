"""Start AiiDA REST API for default profile."""
import os

from aiida.restapi import api
from aiida.restapi.run_api import run_api
from aiida.manage.configuration import load_profile, load_config
from aiida.manage.configuration.profile import Profile
from aiida.manage.manager import get_manager
import aiida.restapi
from aiida.manage.external.postgres import Postgres
import traceback

config = load_config(create=True)

profile_name = os.getenv("AIIDA_PROFILE")

#if profile_name in config.profile_names:

profile = Profile(
    profile_name, {
        "database_hostname":
        os.getenv("AIIDADB_HOST"),
        "database_port":
        os.getenv("AIIDADB_PORT"),
        "database_engine":
        os.getenv("AIIDADB_ENGINE"),
        "database_name":
        os.getenv("AIIDADB_NAME"),
        "database_username":
        os.getenv("AIIDADB_USER"),
        "database_password":
        os.getenv("AIIDADB_PASS"),
        "database_backend":
        os.getenv("AIIDADB_BACKEND"),
        "default_user":
        os.getenv("default_user_email"),
        "repository_uri":
        "file://{}/.aiida/repository/{}".format(os.getenv("AIIDA_PATH"),
                                                profile_name),
    })
config.add_profile(profile)
config.set_default_profile(profile_name)
config.store()


def create_db(profile):
    """Create PostgreSQL database, if missing."""
    dbinfo_su = {
        'host': profile.database_hostname,
        'port': profile.database_port,
        'user': os.getenv("AIIDADB_SUPER_USER"),
        'password': os.getenv("AIIDADB_SUPER_PASS"),
        'database':  'template1',
    }
    postgres = Postgres(interactive=False, quiet=False, dbinfo=dbinfo_su) #, determine_setup=False)

    if not postgres.is_connected:
        raise ConnectionError("Unable to connect as super user")

    try:
        if not postgres.dbuser_exists(dbuser=profile.database_username):
            postgres.create_dbuser(dbuser=profile.database_username, dbpass=profile.database_password)

        if not postgres.db_exists(dbname=profile.database_name):
            postgres.create_db(profile.database_username, profile.database_name)
            
            # Fill DB with vanilla content
            load_profile(profile.name)
            backend = get_manager()._load_backend(schema_check=False)  # pylint: disable=protected-access

            try:
                backend.migrate()
            except Exception as exception:  # pylint: disable=broad-except
                print(
                    'database migration failed, probably because connection details are incorrect:\n{}'.format(exception)
                )

            # Create the user if it does not yet exist
            created, user = orm.User.objects.get_or_create(
                email=profile.default_user, first_name='AiiDA', last_name='EXPLORER', institution='WEBSERVICE'
            )
            if created:
                user.store()
            profile.default_user = user.email

    except:
        print(traceback.format_exc())

if os.getenv("AIIDADB_SUPER_USER"):
    create_db(profile)
    config.update_profile(profile)

load_profile(profile_name)

CONFIG_DIR = os.path.join(
    os.path.split(os.path.abspath(aiida.restapi.__file__))[0], 'common')

(app, api) = run_api(api.App,
                     api.AiidaApi,
                     hostname="localhost",
                     port=5000,
                     config=CONFIG_DIR,
                     debug=False,
                     wsgi_profile=False,
                     hookup=False,
                     catch_internal_server=False)
