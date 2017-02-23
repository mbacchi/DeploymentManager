ResourceManager
======================

ResourceManager is a client library and REST API to control the allocation of resources within a datacenter. The library
requires a MongoDB database for persisting data.

Some example use cases for ResourceManager are tracking IP addresses/ranges, SAN connections, or machine allocations.

Quick Start - CentOS
------
* Install Chef:  ```curl -L https://www.opscode.com/chef/install.sh | bash```
* Download the [cookbook tarball](https://github.com/viglesiasce/resource-manager-cookbook/releases/download/0.2.0/resource-man-cookbooks.tgz)
* Run Chef: ```chef-solo -r resource-man-cookbooks.tgz -o 'recipe[resource-manager]'```

Installation
------
* [Install MongoDB](http://www.mongodb.org/downloads)
* Run mongodb
* Clone this repository
* Install python dependencies: ```pip install Flask Flask-Bootstrap eve PrettyTable argparse requests```
* Run the server: ```cd resource_manager;./server.py```


Data Layout in DB
------
Data is persisted in MongoDB which is a JSON document data store. Machines, public addresses and private
addresses are currently implemented. Public and private addresses share the same schema:

    machine_schema = {
        'hostname': {
            'type': 'string',
            'required': True,
            'unique': True,
        },
        'owner': {
            'type': 'string'
        },
        'state': {
            'type': 'string',
            'allowed': ["pxe", "pxe_failed","idle","needs_repair"]
        }
    }

    address_schema = {
        'address': {
            'type': 'string',
            'required': True,
            'unique': True,
        },
        'owner': {
            'type': 'string'
        }
    }

Interacting with the server
------
A sample client CLI has been constructed in client.py that allows for CRUD operations as follows

    ### List machines (default resource type)
    ./client.py list

    ### Add a machine
    ./client.py create --json '{"hostname":"my-machine", "owner": "tony"}'

    ### Update a machine
    ./client.py update --json '{"hostname":"my-machine", "owner": ""}'

    ### Delete a machine
    ./client.py create --json '{"hostname":"my-machine"}'

    ### List public addresses
    ./client.py list -r public-addresses

This client can also be accessed programatically as a library as follows:

    from resource_manager.client import ResourceManagerClient
    client = ResourceManagerClient()
    client.print_resources()

Exporting and Importing from MongoDB
------

Firstly, the ResourceManager uses the 'eve' database, and he collections are
'machines, 'private-addresses', and 'public-addresses':

```
[root@euca-10-111-54-67 ~]# mongo
MongoDB shell version: 2.6.4
connecting to: test
> show dbs
admin  (empty)
eve    0.078GB
local  0.078GB
> use eve
switched to db eve
> show collections
machines
private-addresses
public-addresses
system.indexes
```

Make sure the database size isn't too large to export, the value to look 
specifically at is dataSize:

```
> db.stats()
{
        "db" : "eve",
        "collections" : 5,
        "objects" : 2019,
        "avgObjSize" : 239.1441307578009,
        "dataSize" : 482832,
        "storageSize" : 1056768,
        "numExtents" : 12,
        "indexes" : 3,
        "indexSize" : 98112,
        "fileSize" : 67108864,
        "nsSizeMB" : 16,
        "dataFileVersion" : {
                "major" : 4,
                "minor" : 5
        },
        "extentFreeList" : {
                "num" : 0,
                "totalSize" : 0
        },
        "ok" : 1
}
```

In order to export the db, follow instructions similar to [DigitalOcean's here](https://www.digitalocean.com/community/tutorials/how-to-import-and-export-a-mongodb-database-on-ubuntu-14-04#exporting-information-from-mongodb):

```
[root@euca-10-111-54-67 ~]# which mongoexport
/usr/bin/mongoexport
[root@euca-10-111-54-67 ~]# mongoexport --db eve -c machines -o evemachines.json
connected to: 127.0.0.1
exported 311 records
[root@euca-10-111-54-67 ~]# mongoexport --db eve -c public-addresses -o evepubips.json
connected to: 127.0.0.1
exported 1598 records
[root@euca-10-111-54-67 ~]# mongoexport --db eve -c private-addresses -o eveprivips.json
connected to: 127.0.0.1
exported 100 records
[root@euca-10-111-54-67 ~]# ls -ltr eve*json
total 527540
-rw-r--r--.  1 root   root       92715 Feb 22 15:33 evemachines.json
-rw-r--r--.  1 root   root      406873 Feb 22 15:34 evepubips.json
-rw-r--r--.  1 root   root       22064 Feb 22 15:34 eveprivips.json
```

You can see it exported 311 records from the machines collection, take note 
of this for the import process.

To import, go to your new MongoDB server (don't do this on the same 
machine!!!) and make sure the mongod service is running:

```
[mbacchi@centos7 DeploymentManager]$ sudo systemctl status mongod
[sudo] password for mbacchi: 
● mongod.service - High-performance, schema-free document-oriented database
   Loaded: loaded (/usr/lib/systemd/system/mongod.service; enabled; vendor preset: disabled)
   Active: active (running) since Wed 2017-02-22 18:44:52 EST; 14h ago
     Docs: https://docs.mongodb.org/manual
  Process: 26157 ExecStartPre=/usr/bin/chmod 0755 /var/run/mongodb (code=exited, status=0/SUCCESS)
  Process: 26154 ExecStartPre=/usr/bin/chown mongod:mongod /var/run/mongodb (code=exited, status=0/SUCCESS)
  Process: 26152 ExecStartPre=/usr/bin/mkdir -p /var/run/mongodb (code=exited, status=0/SUCCESS)
 Main PID: 26163 (mongod)
   CGroup: /system.slice/mongod.service
           └─26163 /usr/bin/mongod --quiet -f /etc/mongod.conf run

Feb 22 18:44:51 centos7 systemd[1]: Starting High-performance, schema-free document-oriented database...
Feb 22 18:44:52 centos7 systemd[1]: Started High-performance, schema-free document-oriented database.
Feb 22 18:44:53 centos7 mongod[26160]: about to fork child process, waiting until server is ready for connections.
Feb 22 18:44:53 centos7 mongod[26160]: forked process: 26163
```

Take the json files from the export and import them thusly:

```
[mbacchi@centos7 DeploymentManager]$ ls -ltr eve*json
total 712
-rw-r--r--. 1 mbacchi mbacchi  92715 Feb 22 18:35 evemachines.json
-rw-r--r--. 1 mbacchi mbacchi  22064 Feb 22 18:35 eveprivips.json
-rw-r--r--. 1 mbacchi mbacchi 406873 Feb 22 18:35 evepubips.json
[mbacchi@centos7 DeploymentManager]$ mongoimport --db eve --collection machines --file evemachines.json
2017-02-22T18:45:44.367-0500	connected to: localhost
2017-02-22T18:45:44.752-0500	imported 311 documents
[mbacchi@centos7 DeploymentManager]$ mongoimport --db eve --collection public-addresses --file evepubips.json
2017-02-22T18:46:10.525-0500	connected to: localhost
2017-02-22T18:46:11.021-0500	imported 1598 documents
[mbacchi@centos7 DeploymentManager]$ mongoimport --db eve --collection private-addresses --file eveprivips.json 
2017-02-22T18:46:31.069-0500	connected to: localhost
2017-02-22T18:46:31.330-0500	imported 100 documents
```

Verify the imported documents match the export above.  Check the new db:

```
[mbacchi@centos7 DeploymentManager]$ mongo
MongoDB shell version v3.4.2
> show databases
admin  0.000GB
eve    0.000GB
local  0.000GB
> use eve
switched to db eve
> show collections
machines
private-addresses
public-addresses

```
