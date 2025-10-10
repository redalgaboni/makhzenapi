# Project Name

API that contains Makhzen data

## Description

This API contains Makhzen data related to Jihate, Wilaya, Amalate/Mukataate, Woulate.

## Installation

- with Docker-compose:

```bash
cd ./Docker-compose

docker-compose -f staging-docker-compose.yaml up -d

```

- data creation
# inside backend container

```bash
alembic revision --autogenerate -m "create jihate,woulate,amalate_jamaate,comments,reactions tables"
alembic upgrade head

# Import reference data
python -m backend.app.cli.jihate_import
python -m backend.app.cli.amalate_jamaate_import
python -m backend.app.cli.woulate_import

# create random reactions and comments
python -m backend.app.cli.generate_random_reactions_comments

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
