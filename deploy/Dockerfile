FROM python:3.10-bullseye

RUN apt-get update && apt-get install -y \
    bluez \
    bluez-meshd \
    dbus

COPY entrypoint.sh .
CMD ./entrypoint.sh