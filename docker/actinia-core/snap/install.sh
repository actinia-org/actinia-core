# /bin/sh

# https://senbox.atlassian.net/wiki/spaces/SNAP/pages/30539778/Install+SNAP+on+the+command+line
# https://senbox.atlassian.net/wiki/spaces/SNAP/pages/30539785/Update+SNAP+from+the+command+line

# set JAVA_HOME (done in Docker as well)
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# install module 'jpy' (A bi-directional Python-Java bridge)
git clone https://github.com/bcdev/jpy.git /src/snap/jpy
pip3 install wheel
(cd /src/snap/jpy && python3 setup.py bdist_wheel)
# hack because ./snappy-conf will create this dir but also needs *.whl files...
mkdir -p /root/.snap/snap-python/snappy
cp /src/snap/jpy/dist/*.whl "/root/.snap/snap-python/snappy"

# install and update snap
wget -q -O /src/snap/esa-snap_all_unix_6_0.sh \
  "http://step.esa.int/downloads/6.0/installers/esa-snap_all_unix_6_0.sh"
sh /src/snap/esa-snap_all_unix_6_0.sh -q -varfile /src/snap/response.varfile
/usr/local/snap/bin/snap --nosplash --nogui --modules --update-all

# create snappy and python binding with snappy
/usr/local/snap/bin/snappy-conf /usr/bin/python3
(cd /root/.snap/snap-python/snappy && python3 setup.py install)

# test
/usr/bin/python3 -c 'from snappy import ProductIO'
