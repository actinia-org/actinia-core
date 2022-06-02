FROM mundialis/actinia-core:latest

# # Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# # Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=actinia_core.main
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV DEFAULT_CONFIG_PATH=/etc/default/actinia

RUN pip3 uninstall actinia-core -y
RUN pip3 uninstall actinia_core -y

COPY docker/actinia-core-dev/actinia.cfg /etc/default/actinia
COPY . /src/actinia_core/

RUN git config --global --add safe.directory /src/actinia*

WORKDIR /src/actinia_core/
RUN pip3 install -e .
