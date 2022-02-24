# drogue-ble-mesh-gateway

## Getting started

* Initialize two devices using this procedure https://gist.github.com/dejanb/85282932d08d26dce2c9323b3d0cc1e2 and save the token.

Generate pub/sub connection between them. Let's say the first device have address `00aa` and the other one `00ae`, `00aa` will simulate a device and `00ae` a gateway.

* Create a pub setting for a device

```
pub-set 00aa C002 0 50 5 1000
```

* Create a subscription for a gateway.

```
sub-add 00ae c002 1000
```

* Configure gateway cloud credentials by editing `username` and `password` variables in `gateway.py`

* Now you can start device and gateway with their tokens like,

```
./gateway.py 159d79164ebff7f1
```

```
./device.py 62cb5d464413e5c7
```

* The device should be emitting status every 15 secs and gateway should forward that to the cloud.

You should be able to see data in the cloud like (change the name of the `example-app`)

```
websocat wss://ws-integration.sandbox.drogue.cloud/example-app -H="Authorization: Bearer $(drg whoami -t)" | jq '.data_base64 |= @base64d'
```

* You can provision a third device next and use it change a state of the `00aa` device using `test-mesh`