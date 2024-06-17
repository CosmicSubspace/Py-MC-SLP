# Py-MC-SLP
Implements Minecraft's Server List Ping protocol in a simple Python script.

## Usage
```
import pymcslp
resp=pymcslp.get_mc_server_status("mc.hypixel.net")
print(resp["description"])
```
