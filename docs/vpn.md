Mesos Grid VPN Access
------------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl -X http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure and get _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${grid_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${grid_name}.ovpn file
6. Import this config into Tunnelblick by double clicking on ovpn file
7. Connect to VPN using credentials from step 3)
8. Following services are available

Mesos:
```
http://leader.mesos.service.${grid_name}:5050/
```
Marathon:
```
http://leader.mesos.service.${grid_name}:18080/
```
Consul:
```
http://leader.mesos.service.${grid_name}:8500/
```

DCOS Grid VPN Access
-----------------------

OpenVPN for MacOS Setup:

1. Install Tunnelblick
2. go to curl http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/infrastructure and save _accessip parameter
3. ssh to _accessip, and create there some users and passwd them, using commands adduser/passwd respectively, eg:

```adduser vpnuser1```

```passwd vpnuser1```

3. get OpenVPN config:
```
echo -e `curl -qs http://localhost:5555/api/v2.0/grids/${grid_name}/deployment/vpn | tr -d '"'`
```
4. Save config as ${grid_name}.ovpn file
5. ssh to _accessip and save /etc/openvpn/keys/ca.crt near ${grid_name}.ovpn file
6. Import this config into Tunnelblick by double clicking on ovpn file
7. Connect to VPN using credentials from step 3)
8. Following services are available

DCOS GUI:
```
http://192.168.164.1/
```
Mesos:
```
http://192.168.164.1/mesos/
```
Marathon:
```
http://192.168.164.1/marathon/
```

