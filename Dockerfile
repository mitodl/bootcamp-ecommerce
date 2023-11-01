FROM python:3.9.13
LABEL maintainer "ODL DevOps <mitx-devops@mit.edu>"


# Add package files, install updated node and pip
WORKDIR /tmp

COPY apt.txt /tmp/apt.txt
RUN apt-get update
RUN apt-get install -y $(grep -vE "^\s*#" apt.txt  | tr "\n" " ")

# pip
RUN curl --silent --location https://bootstrap.pypa.io/get-pip.py | python3 -
RUN pip install -U pip-tools

# Add, and run as, non-root user.
RUN mkdir /app
RUN adduser --disabled-password --gecos "" mitodl
RUN mkdir /var/media && chown -R mitodl:mitodl /var/media

ENV  \
  # poetry:
  POETRY_VERSION=1.5.1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/tmp/cache/poetry' \
  POETRY_HOME='/home/mitodl/.local' \
  VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$POETRY_HOME/bin:$PATH"

# Install project packages
# COPY requirements.txt /tmp/requirements.txt
# COPY test_requirements.txt /tmp/test_requirements.txt
# RUN pip install -r requirements.txt -r test_requirements.txt

COPY pyproject.toml /app
COPY poetry.lock /app
RUN chown -R mitodl:mitodl /app
RUN mkdir ${VIRTUAL_ENV} && chown -R mitodl:mitodl ${VIRTUAL_ENV}

USER mitodl
RUN curl -sSL https://install.python-poetry.org \
  | \
  POETRY_VERSION=${POETRY_VERSION} \
  POETRY_HOME=${POETRY_HOME} \
  python3 -q
WORKDIR /app
RUN python3 -m venv $VIRTUAL_ENV
RUN poetry install

# Add project
COPY . /app

# Gather static
USER root
RUN apt-get clean && apt-get purge

USER mitodl

# Set pip cache folder, as it is breaking pip when it is on a shared volume
ENV XDG_CACHE_HOME /tmp/.cache

EXPOSE 8099
ENV PORT 8099
CMD uwsgi uwsgi.ini
