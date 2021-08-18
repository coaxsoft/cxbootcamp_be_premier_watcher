# Premier Watcher

## Project scope

Application example of COAX Python Bootcamp project explained in lectures.

## Environment

[Link](.docs/.env.example) to the example of environments

## Runtime environment

The infrastructure of Optinet project consists of the following services:

* Premier Watcher project application (monolith)
* PostgreSQL database
* Celery
* Redis
* Docker
* ElasticSearch
* SMTP for mails

## Commands

```
# Run non-applied migrations
python manage.py migrate

# Collect static into Storage
python manage.py collectstatic --no-input

# When ES enabled, use this command to rebuild indices
python manage.py search_index --rebuild

# Create superuser
python manage.py createsuperuser

# To enter interactive Django shell
python manage.py shell -i=python
```

## Development environment

### Docker setup

1. Install the docker and docker-compose.
2. Create the directory `.env` in the root project directory and paste the file `vars`
inside the `.env`. Put the needed [environments](.docs/.env.example) to `vars`.
3. Run the project

```
docker-compose -f docker-compose.dev.yml up --build
```

### Manual setup

#### 1. Requirements:

1. Install Python 3.9
2. Install PostgreSQL 12.3
3. Install Redis 6.2.5
4. Install ElasticSearch

#### 2. Install the project packages by command:

```
pipenv install
```

#### 3. Collect static files

```
python manage.py collectstatic
```

#### 4. Run migrations

```
python manage.py migrate --no-input
```

#### 5. Run the project

```
python manage.py runserver
```

## Test environment

### Tests

#### Environments

```
ELASTICSEARCH_DSL_AUTO_REFRESH=False
ELASTICSEARCH_DSL_SIGNAL_PROCESSOR=index.signals.FakeSignalProcessor
```

#### Description

For testing purposes we need all variables defined above.
We need to set `ELASTICSEARCH_DSL_AUTO_REFRESH=False` not to force tests run very slowly.
We need to set `ELASTICSEARCH_DSL_SIGNAL_PROCESSOR=index.signals.FakeSignalProcessor` to force tests
run as usual.

### Linter

#### Run

```
flake8 .
```

## Notes

...
