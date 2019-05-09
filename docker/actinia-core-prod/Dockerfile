FROM mundialis/actinia-core:latest

# Copy actinia config file and start scripts
COPY actinia.cfg /etc/default/actinia
COPY start.sh /src/start.sh

WORKDIR /src/actinia_core
RUN python3 setup.py install

EXPOSE 8088
EXPOSE 9191

ENTRYPOINT ["/bin/bash"]
CMD ["/src/start.sh"]
