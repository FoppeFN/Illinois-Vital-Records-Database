# Generating & Using Mock Data

## Generation

1. Open a shell inside the Docker web container using `docker compose exec web bash`
2. Generate the mock data by running `python manage.py generate_family` inside the shell. This data will be stored in `data/mock/family_tree.json`

#### Parameters (Optional)

- FTDL (Family Tree Depth Limit): Sets the depth limit for the family tree generated.
- SPDL (Sibling-Partner Depth Limit): Sets the breadth limit for the family tree generated.
- PCP: The odds that an individual is married.
- CD_MEAN: The mean number of children per marriage.
- CD_SD: The standard deviation in number of children per marriage.
- MAX_CHILDREN: The maximum number of children per marriage.
- min_age: The minimum age of death.
- max_age: The maximum age of death.
- mean_age: The average age of death.
- birth_date_seed: The date at which generation begins. Generation generally trends backwards in time from this date.
- young_offset: The average number of years younger a child will be than their parent.
- old_offset: The average number of years older a parent will be than their child.

## Populating the Database

1. Stage initial migrations to the database by running `python manage.py makemigrations` inside the shell.
2. Finalize migrations to the database by running `python manage.py migrate` inside the shell.
3. Initialize the database with Illinois counties and some cities by running `python manage.py init_db` inside the shell.
4. Populate the database with the generated mock data by running `python manage.py mock_populate` inside the shell. This may take a bit depending on given [parameters](parameters-optional).

## Errors

If an error occurs, the easiest fix is usually to reset the database via the following procedure, then retry from scratch. (WARNING: THIS PROCEDURE WILL ERASE ALL DATABASE CONTENT):

1. Delete the contents of the records/migrations folder by running `rm records/migrations/*` from the root directory.
2. Compose down the Docker container using `docker compose down -v` in the shell.
3. Create a new file called `__init__.py` within the records/migrations folder by running `touch records/migrations/__init__.py` from the root directory.
4. Compose up the Docker container using `docker compose up --build`
5. Repeat [generation](#generation) and [populating](#populating-the-Database).
6. If errors persist, see other documentation.