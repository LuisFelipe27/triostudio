# start from an official image
FROM python:3.7.4

# arbitrary location choice: you can change the directory
RUN mkdir -p /opt/apps/triostudio
WORKDIR /opt/apps/triostudio

# install our dependencies
# we use --system flag because we don't need an extra virtualenv
COPY Pipfile Pipfile.lock /opt/apps/triostudio/
RUN pip3 install pipenv && pipenv install --system
RUN pip3 install channels
RUN pip3 install drf-spectacular
RUN pip3 install drf-spectacular-sidecar
RUN pip3 install channels-redis
RUN pip3 install openpyxl
RUN pip3 install odfpy
RUN pip3 install django-import-export==2.6.1
RUN pip3 install python-magic
RUN pip3 install boto3 --upgrade
RUN pip3 install twilio
RUN pip3 install imgurpython
RUN pip3 install datedelta
RUN pip3 install pypdf2
RUN pip3 install Jinja2==2.11.3
RUN pip3 install MarkupSafe==2.0.1
RUN pip3 install xlsxwriter
RUN pip3 install Pillow
RUN pip3 install django-tenant-schemas==1.11.0
RUN pip3 install django-two-factor-auth==1.13.2
RUN pip3 install phonenumbers==8.12.49
RUN pip3 install django-admin-autocomplete-filter
RUN pip3 install django-auditlog
RUN pip3 install xmltodict
RUN pip3 install django-mailbox
RUN pip3 install django-pwa
RUN pip3 install djangorestframework-datatables
RUN pip3 install django-simple-sso
RUN pip3 install pytesseract==0.3.10
# importlib_metadata >= 3.6 changed entry_points() from dict to EntryPoints;
# kombu 5.2.x (Python 3.7 max compat) still uses the old dict-style API.
RUN pip3 install "importlib_metadata<3.6"
RUN pip3 install celery==5.2.7
RUN pip3 install redis==4.5.5
RUN pip3 install kombu==5.2.4
# Re-pin to ensure kombu didn't pull a newer importlib_metadata
RUN pip3 install "importlib_metadata<3.6"

# change repos 
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/99no-check-valid-until

RUN apt-get update

# install gettext
RUN apt-get install -y gettext

# # install libreoffice
# RUN apt-get install -y libreoffice

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

ARG USING_CACHE=1
ARG PORT_EXPOSE
RUN echo "gunicorn -c config/gunicorn/conf.py --chdir /opt/apps/triostudio --bind :$PORT_EXPOSE config.wsgi:application" > /opt/apps/gunicorn_init.sh

# copy our project code
COPY . /opt/apps/triostudio

# RUN python3 manage.py collectstatic --no-input
# && python3 manage.py migrate  # <-- here

# define the default command to run when starting the container
CMD ["sh", "/opt/apps/gunicorn_init.sh"]
