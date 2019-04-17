FROM mundialis/actinia-core

# Copy actinia config file and start scripts
COPY actinia.cfg /etc/default/actinia

WORKDIR /src/actinia_core
RUN python3 setup.py install

EXPOSE 8088
EXPOSE 9191

ENTRYPOINT ["/bin/bash"]
CMD ["/src/start.sh"]
