FROM fluent/fluentd
RUN ["gem", "install", "fluent-plugin-elasticsearch", "--no-rdoc", "--no-ri", "--version", "3.5.5"]
RUN rm /fluentd/etc/fluent.conf
COPY fluent.conf /fluentd/etc
