#!/bin/bash

service dbus start
#service bluetooth start

/usr/libexec/bluetooth/bluetooth-meshd --nodetach --debug


