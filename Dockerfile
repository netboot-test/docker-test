# Pull base image.
FROM python:3.5.2

# File Author / Maintainer
LABEL MAINTAINER="Contact@thomas-illiet.fr"

# Copy a configuration file from the current directory
ADD . /code
RUN pip install -r /code/requirements.txt

WORKDIR /code/beapi
VOLUME /code

ENTRYPOINT bash -c "python manage.py runserver"
