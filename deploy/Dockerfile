FROM python:3.10-slim

# add testing repo to pick up bluez 5.62
# NOTE: picking up dbus from there, too
COPY testing-source.list /etc/apt/sources.list.d/

RUN apt-get update && apt-get install -t testing -y \
    bluez \
    bluez-meshd \
    dbus

RUN rm -rf /var/lib/bluetooth/mesh

COPY mesh /var/lib/bluetooth/mesh

COPY entrypoint.sh .

CMD ./entrypoint.sh
