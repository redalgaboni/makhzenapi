FROM python:3.12 AS compile-image

WORKDIR /code

COPY ./Docker/requirements.txt /code/requirements.txt

RUN pip install --user --upgrade setuptools
RUN pip install --user -r /code/requirements.txt

FROM python:3.12-slim AS build-image

ARG USER=genzuser
ARG GROUP=genzuser
ARG UID=788
ARG GID=788

COPY --from=compile-image /root/.local /home/${USER}/.local

ENV PATH=/home/${USER}/.local/bin:$PATH
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
#COPY . /code/
COPY ./Docker/entrypoint.sh /entrypoint.sh

# Create non-root user
RUN groupadd -g ${GID} ${GROUP} \
    && useradd -u ${UID} -g ${GROUP} -m ${USER}
RUN chown -R ${USER}:${GROUP} /code


USER genzuser