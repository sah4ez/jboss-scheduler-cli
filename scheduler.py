#!/usr/local/bin/python3.6

import sys
import logging
import os
import errno
import getpass
import lxml.etree as ET
from MBean import MBean
from list_bean import ListMBeans


def create_log(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


scheduler_filename = 'scheduler-service.xml'


def list_beans(params):
    path = scheduler_filename
    if len(params) == 2 and os.path.exists(params[1]):
        path = params[1]
    if len(params) < 1 or len(params) > 2:
        print('scheduler list - if file "scheduler-service.xml" in current directory or\n'
              'scheduler list <path_to_file> to specific path')
        exit(1)
    lb = ListMBeans(path)
    lb.parse()
    lb.print()
    exit(0)


def disable_bean(params):
    path = scheduler_filename
    size = len(params)
    if size >= 3 and os.path.exists(params[size - 1]):
        path = params[size - 1]
    if len(params) < 2:
        print('scheduler disable <name_mbean> - if file "scheduler-service.xml" in current directory or\n'
              'scheduler disable <name_mbean> <path_to_file> to specific path')
        exit(1)
    lb = ListMBeans(path)
    if os.path.exists(params[size - 1]):
        lb.disable(params[1:size - 1])
    else:
        lb.disable(params[1:])
    print('MBean was disable')
    exit(0)


def enable_bean(params):
    path = scheduler_filename
    size = len(params)
    if size >= 3 and os.path.exists(params[size - 1]):
        path = params[size - 1]
    if len(params) < 2:
        print('scheduler enable <name_mbean> - if file "scheduler-service.xml" in current directory or\n'
              'scheduler enable <name_mbean> <path_to_file> to specific path')
        exit(1)
    lb = ListMBeans(path)
    if os.path.exists(params[size - 1]):
        lb.enable(params[1:size - 1])
    else:
        lb.enable(params[1:])
    print('MBean was enable')
    exit(0)


def tcreate(params):
    path = scheduler_filename
    if len(params) == 2 and os.path.exists(params[1]):
        path = params[1]
    if len(params) < 1 or len(params) > 2:
        print('scheduler tcreate - if file "scheduler-service.xml" in current directory or\n'
              'scheduler tcreate <path_to_file> to specific path')
        exit(1)

    lb = ListMBeans(path)
    lb.parse()

    mbean = MBean()
    if not os.path.exists(os.path.expanduser('~') + '/.local/bin/scheduler/template.xml'):
        print('Not found template.xml in $HOME/.local/bin/scheduler/')
        exit(1)
    mbean.template(os.path.expanduser('~') + '/.local/bin/scheduler/template.xml')
    mbean.name = input('Enter name MBean: ')

    startup = input('Enter name MBean (true/false): ')
    while startup not in ['true', 'false']:
        startup = input('Enter name MBean (true/false): ')
    mbean.start_at_startup = bool(startup)

    value = input('Enter taskCommander (%s)?: ' % mbean.schedulable_arguments[0])
    if value.strip() != '':
        mbean.schedulable_arguments.pop(0)
        mbean.schedulable_arguments.insert(value, 0)

    value = input('Enter user (%s)?: ' % mbean.schedulable_arguments[1])
    if value.strip() != '':
        mbean.schedulable_arguments.pop(1)
        mbean.schedulable_arguments.insert(1, value)

    value = getpass.getpass('Enter passwd (use default)?: ')
    if value != '':
        mbean.schedulable_arguments.pop(2)
        mbean.schedulable_arguments.insert(2, value)

    value = input('Enter name event: ')
    while value == '':
        value = input('Enter name event: ')
    mbean.schedulable_arguments.pop(3)
    mbean.schedulable_arguments.insert(3, value)

    value = input('Enter arguments value: ')
    while value == '':
        value = input('Enter arguments value: ')
    mbean.schedulable_arguments.pop(4)
    mbean.schedulable_arguments.insert(4, value)

    value = input('Enter InitialStartDate in format "M/d/yy h:mm a" or (%s)?: ' % mbean.initial_start_date)
    if value != '':
        mbean.initial_start_date = str(value)

    value = input('Enter SchedulePeriod (%s)?: ' % mbean.schedule_period)
    if value != '':
        mbean.schedule_period = int(value)

    value = input('Enter InitialRepetitions (%s)?: ' % mbean.initial_repetitions)
    if value != '':
        mbean.initial_repetitions = int(value)

    print('You enter MBean:')
    print(ET.tostring(mbean.xml(), pretty_print=True).decode())
    value = input('All right (y/n)?: ')
    while value not in ['y', 'yes', 'n', 'no']:
        value = input('All right (y/n)?: ')

    if value == 'y' or value == 'yes':
        lb.mbeans.append(mbean.xml())
        lb.save()
    else:
        tcreate(params)
    exit(0)


def create(params):
    path = scheduler_filename
    if len(params) == 2 and os.path.exists(params[1]):
        path = params[1]
    if len(params) < 1 or len(params) > 2:
        print('scheduler create - if file "scheduler-service.xml" in current directory or\n'
              'scheduler create <path_to_file> to specific path')
        exit(1)

    lb = ListMBeans(path)
    lb.parse()

    mbean = MBean()

    value = input('Enter args name MBean (schedule=%s)?: ')
    if value == '':
        value = 'schedule=%s'
    mbean.mbean_name = value

    value = input('Enter name MBean: ')
    while value == '':
        value = input('Enter name MBean: ')
    mbean.name = value

    value = input('Enter code MBean(org.jboss.varia.scheduler.Scheduler): ')
    if value == '':
        value = 'org.jboss.varia.scheduler.Scheduler'
    mbean.mbean_code = value

    value = input('Enter depend: ')
    while value != '':
        mbean.depends.append(value)
        value = input('Enter next depend (empty for next step): ')

    value = input('Enter name MBean (true/false): ')
    while value not in ['true', 'false']:
        value = input('Enter name MBean (true/false): ')
    mbean.start_at_startup = bool(value)

    value = input('Enter SchedulableClass MBean: ')
    while value == '':
        value = input('Enter SchedulableClass MBean: ')
    mbean.schedulable_class = value

    value = input('Use default SchedulableArguments? (y/n): ')
    if value in ['y', 'yes']:
        task_commander = 'SystemTasksCommander'
        value = input('Enter taskCommander (%s)?: ' % task_commander)
        if value.strip() != '':
            mbean.schedulable_arguments.append(value)
        else:
            mbean.schedulable_arguments.append(task_commander)

        user = 'system'
        value = input('Enter user (%s)?: ' % user)
        if value.strip() != '':
            mbean.schedulable_arguments.append(value)
        else:
            mbean.schedulable_arguments.append(user)

        value = getpass.getpass('Enter passwd?: ')
        while value == '':
            value = getpass.getpass('Set empty passwd?: ')
            if value == '':
                break
        mbean.schedulable_arguments.append(value)

        value = input('Enter name event: ')
        while value == '':
            value = input('Enter name event: ')
        mbean.schedulable_arguments.append(value)

        value = input('Enter arguments value: ')
        while value == '':
            value = input('Enter arguments value: ')
        mbean.schedulable_arguments.append(value)

        value = input('Use java.lang.String for each arguments (y/n)?: ')
        if value in ['y', 'yes']:
            for arg in mbean.schedulable_arguments:
                mbean.schedulable_argument_types.append('java.lang.String')
        else:
            for arg in mbean.schedulable_arguments:
                value = input('Enter type for %s: ' % arg)
                while value == '':
                    value = input('Enter type for %s: ' % arg)
                mbean.schedulable_argument_types.append(value)
    else:
        args = input('Enter args (empty for next step): ')
        while args != '':
            arg_type = input('Enter type args: ')
            while arg_type == '':
                arg_type = input('Can\'t be empty. Enter type args: ')
            mbean.schedulable_arguments.append(args)
            mbean.schedulable_argument_types.append(arg_type)
            args = input('Enter next arg (empty for next step): ')

    value = input('Enter InitialStartDate in format "M/d/yy h:mm a" or (NOW)?: ')
    if value != '':
        mbean.initial_start_date = str(value)
    else:
        mbean.initial_start_date = str('NOW')

    value = input('Enter SchedulePeriod (86400000)?: ')
    if value != '':
        mbean.schedule_period = int(value)
    else:
        mbean.schedule_period = int(86400000)

    value = input('Enter InitialRepetitions (-1)?: ')
    if value != '':
        mbean.initial_repetitions = int(value)
    else:
        mbean.initial_repetitions = int(-1)

    print('You enter MBean:')
    print(ET.tostring(mbean.xml(), pretty_print=True).decode())
    value = input('All right (y/n)?: ')
    while value not in ['y', 'yes', 'n', 'no']:
        value = input('All right (y/n)?: ')

    if value == 'y' or value == 'yes':
        lb.mbeans.append(mbean.xml())
        lb.save()
    else:
        create(params)
    exit(0)


def edit(params):
    path = scheduler_filename
    if len(params) == 5 and os.path.exists(params[4]):
        path = params[4]
    if len(params) < 4 or len(params) > 5:
        print('scheduler edit <name> <arg> <value> - if file "scheduler-service.xml" in current directory or\n'
              'scheduler edit <name> <arg> <value> <path_to_file> to specific path')
        exit(1)

    lb = ListMBeans(path)
    lb.update(name=params[1], arg=params[2], value=params[3])
    find_bean(['find', params[1], params[4]])


def find_bean(params):
    path = scheduler_filename
    if len(params) == 3 and os.path.exists(params[2]):
        path = params[2]
    if len(params) < 2 or len(params) > 3:
        print('scheduler find <name> - if file "scheduler-service.xml" in current directory or\n'
              'scheduler find <name> <path_to_file> to specific path')
        exit(1)
    lb = ListMBeans(path)
    is_active, bean = lb.find(params[1])
    if bean is None:
        print('Not found Bean')
    else:
        print(is_active, ':\n', ET.tostring(bean, pretty_print=True).decode())


def help():
    print("scheduler COMMAND [path_to_file]")
    print()
    print("  list - print list all MBeans")
    print()
    print("  disable NAME - disable specific MBean")
    print()
    print("  enable NAME - enable specific MBean")
    print()
    print("  create - dialogue for create MBean")
    print()
    print("  tcreate - dialogue for create MBean from template.xml in current directory")
    print()
    print("  edit NAME <arg> <value> - change specific attribute")
    print("\n  specific edit command:")
    print("    edit event <arg> <value> - change value Event.class")
    print("    edit args <arg> <value> - change value attributes of Event.class")
    print()
    print("  find NAME - print found MBean")


logging.basicConfig()
LOG = logging.getLogger("SCHEDULER")
LOG.setLevel(logging.ERROR)
log_path = "/var/log/scheduler/all.log"
create_log(log_path)
file = logging.FileHandler(filename=log_path)
LOG.addHandler(file)


def main(args):
    if len(args[1:]) < 1:
        print("Invalid command")
        help()
        exit(1)

    LOG.info('exec: scheduler ' + " ".join(args[1:]))
    command = args[1]
    if command == "help":
        help()
        exit(0)
    elif command == "list":
        list_beans(args[1:])
    elif command == "disable":
        disable_bean(args[1:])
    elif command == "enable":
        enable_bean(args[1:])
    elif command == "tcreate":
        tcreate(args[1:])
    elif command == "create":
        create(args[1:])
    elif command == "edit":
        edit(args[1:])
    elif command == "find":
        find_bean(args[1:])
    else:
        print("Invalid command")
        help()
        exit(1)


if __name__ == '__main__':
    main(sys.argv)
