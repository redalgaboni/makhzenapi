# Project Name

API containing Morocco Makhzen data.

## Description

This API contains Morocco Makhzen data related to Jihate, Wilaya, Amalate/Mukataate, Woulate.

تحتوي واجهة برمجة التطبيقات هذه على بيانات المغرب - المخزن المتعلقة بولاة و عمال مختلف الجهات والولايات والعمالات.

## Installation

- with Docker-compose:

```bash
cd ./Docker-compose

docker-compose -f staging-docker-compose.yaml up -d

```

- data creation : managed by alembic with entrypoint

### Create random reactions data

In backend container:
```bash
# create 3 users at least
python -m backend.app.cli.create_user \
  --email user3@example.com \
  --username user3

# create random reactions and comments ( script needs at least 3 different users)
python -m backend.app.cli.generate_random_reactions_comments

```

### In Case of alembic issues while data exists in DB

```bash
DROP TABLE alembic_version;
alembic revision --autogenerate -m "initial"
alembic stamp head
alembic revision --autogenerate -m "..." #refine tables in case
alembic upgrade head
```

## Usage

Instructions on how to use the project, including any commands or configurations.

## Features

- Feature 1
- Feature 2
- Feature 3

## Contributing

Guidelines for contributing to the project, including how to set up a development environment and submit pull requests.

Project follow a gitflow model:

`feature/` --> `staging` --> `main`

- `feature/` for new features
- `bugfix/` for bug fixes
- `hotfix/` for hotfixes

Ex: A new feature developed in the `feature/XYZ` branch should PRed to the `staging` branch.

## License

Information about the project's license.

## Credits

Acknowledgments for any resources used, including libraries or APIs.


## Contact

How users can get in touch with the project maintainers.
Email: redalgaboni@tutamail.com
