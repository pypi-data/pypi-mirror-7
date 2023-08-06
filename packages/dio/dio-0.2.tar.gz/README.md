# Dio
## A package for managing and backing up your digitalocean droplets
based off [https://github.com/koalalorenzo/python-digitalocean](https://github.com/koalalorenzo/python-digitalocean)


## How to install

You can install python-dio using **pip**

    pip install -U dio

or via sources:

    python setup.py install


## Features
* **DROPLET BACKUP!!! (rsync and snapshot a droplet)**
* **Uses digitalocean v2.0 API**
* Get user's Droplets
* Get user's Images (Snapshot and Backups)
* Get public Images
* Get Droplet's event status
* Create and Remove a Droplet
* Resize a Droplet
* Shutdown, restart and boot a Droplet
* Power off, power on and "power cycle" a Droplet
* Perform Snapshot
* Enable/Disable automatic Backups
* Restore root password of a Droplet


### Example cronjob:

```sh
# DigitalOcean backup script
30 * * * * /usr/bin/python /Users/username/bin/backup.py
```

### Example usage:

```python

import dio

""" Your digitalocean API v2.0 token """
token = "YOUR_TOKEN"

""" Ignore list of droplets to bypass in operations """
ignore = ["production.example.com"]

""" Droplet backup options. Only needed when doing backup """
options = {
  "dev.example.com": {
    "ssh_user"        : "root",
    "ssh_key"         : "ssh_key",
    "backup_dir"      : "/Users/username/Droplets",
    "remote_dir"      : "/root",
    "use_ip"          : True,
    "snapshot_hour"   : 3,
    "snapshots_keep"  : 2,
    "snapshot_delete" : True,
  },
  "production.example.com": {
    "ssh_user"        : "root",
    "ssh_key"         : "ssh_key",
    "backup_dir"      : "/Users/username/Droplets",
    "remote_dir"      : "/var/www",
    "use_ip"          : True,
    "snapshot_hour"   : 3,
    "snapshots_keep"  : 7,
    "snapshot_delete" : True,
  }
}

""" Manager init will automaticly get the droplets """
manager = dio.Manager( token, ignore )

""" backup your droplet with rsync """
for droplet in manager.droplets:
  dio.Backup( options, droplet )

""" See how many api calls you used """
print dio.api.calls

""" See how many remaining api calls you have left for the hour """
print dio.api.remaining

```