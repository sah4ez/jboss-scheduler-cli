# jboss-scheduler-cli
Simple CLI for edit scheduler-service.xml in JBoss server.

# Install
Run `install.sh`. 

# About
Base dir for scheduler-tool: `$HOME/.local/bin/scheduler/`
For loggin use path: **/var/log/scheduer/all.log**
Check exist it, or create.

If you whant use tmplate for create MBean in your scheduler-service, you can edit template.xml in Base dir.

# Depends
- lxml=3.8.0
- Python3.6

# Issues
If you have **ImportError etree**, please check package: `libxslt` and `libxml2`
Header of `scheduler.py` contains `#!/usr/local/bin/python3.6`

# How use
`>$ scheduler-tool help`
```
scheduler COMMAND [path_to_file]
if scheduler-service.xml exist in current dir path_to_file can be empty.

COMMAND:

  list - print list all MBeans

  disable NAME - disable specific MBean

  enable NAME - enable specific MBean

  create - dialogue for create MBean

  tcreate - dialogue for create MBean from template.xml in Base dir

  edit NAME <arg> <value> - change specific attribute

  specific edit command:
    edit event <arg> <value> - change value Event.class
    edit args <arg> <value> - change value attributes of Event.class

  find NAME - print found MBean

```
