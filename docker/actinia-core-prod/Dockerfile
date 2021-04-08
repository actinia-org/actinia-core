FROM mundialis/actinia-core:0.99

COPY actinia.cfg /etc/default/actinia
COPY start.sh /src/start.sh

# Let actinia run as non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN addgroup -g $GROUP_ID user
RUN adduser -D -g '' -u $USER_ID -G user user
RUN chown -R user:user /src/

USER user
