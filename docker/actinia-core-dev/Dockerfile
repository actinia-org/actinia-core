FROM mundialis/actinia-core:g79-latest-alpine

COPY actinia.cfg /etc/default/actinia

RUN pip3 uninstall actinia-core -y

# for actinia-gdi development
#RUN pip3 uninstall actinia-gdi.wsgi -y
#WORKDIR /src/actinia-gdi
