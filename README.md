# aiida-restapi-container

This container runs an AiiDA REST API.

It does *not* run postgres or rabbitmq inside the container, but rather:

 * connects to an external postgres database for querying
 * mounts the AiiDA file repository

Credentials for connecting to the postgres DB are provided via environment variables.

## Building the docker image
```
docker build . -t aiida-1.2.1-restapi --build-arg AIIDA_VERSION=1.2.1
```
All variables except the AiiDA version can be set at run time

## Running the docker container

Place environment variables in a file `.env`:
```
AIIDADB_HOST=host.docker.internal
AIIDADB_PORT=5432
AIIDADB_NAME=curated_cofs_aiida1
AIIDADB_USER=mcloud
AIIDADB_PASS=mypass
AIIDADB_BACKEND=django
# optional, for creating database
AIIDADB_SUPER_USER=admin
AIIDADB_SUPER_PASS=myadminpass
```

and run
```
docker run -d --name restapi --env-file .env  -p 5678:80 aiida-restapi
```
then try e.g.
```
curl localhost:5678/api/v4/users
docker rm -f restapi
```
