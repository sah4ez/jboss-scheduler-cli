#!/usr/bin/python3.6

import lxml.etree as ET


class MBean:
    def __init__(self):
        self.name = ''
        self.start_at_startup = False
        self.depends = list()
        self.schedulable_arguments = list()
        self.schedulable_argument_types = list()
        self.initial_start_date = 'NOW'
        self.schedule_period = 1000 * 60 * 60 * 24  # every day
        self.initial_repetitions = -1
        self.mbean_code = 'org.jboss.varia.scheduler.Scheduler'
        self.mbean_name = 'scheduler=%s'
        self.schedulable_class = ''

    def template(self, path):
        self.name = ''
        tree = ET.parse(path)
        root = tree.getroot()
        self.depends = list()
        self.schedulable_arguments = list()
        self.schedulable_argument_types = list()
        mbean_tag = root.find('mbean')
        self.mbean_code = mbean_tag.attrib['code']
        name_arr = str(mbean_tag.attrib['name']).strip().split('=')
        name_arr[len(name_arr)-1] = '%s'
        self.mbean_name = "=".join(name_arr)

        for dep in root.iter('depends'):
            self.depends.append(dep.text.strip())

        for tag in root.iter('attribute'):
            if tag.attrib['name'] == 'StartAtStartup':
                self.start_at_startup = bool(tag.text)

            if tag.attrib['name'] == 'SchedulableClass':
                self.schedulable_class = tag.text

            if tag.attrib['name'] == 'SchedulableArguments':
                for element in str(tag.text).split(','):
                    self.schedulable_arguments.append(element.strip())

            if tag.attrib['name'] == 'SchedulableArgumentTypes':
                for element in str(tag.text).split(','):
                    self.schedulable_argument_types.append(element.strip())

            if tag.attrib['name'] == 'InitialStartDate':
                self.initial_start_date = tag.text

            if tag.attrib['name'] == 'SchedulePeriod':
                self.schedule_period = tag.text

            if tag.attrib['name'] == 'InitialRepetitions':
                self.initial_repetitions = tag.text


    def xml(self):
        root = ET.Element('mbean')
        root.attrib['code'] = self.mbean_code
        root.attrib['name'] = self.mbean_name % self.name

        for depend in self.depends:
            dep = ET.Element('depends')
            dep.text = depend
            root.append(dep)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'StartAtStartup'
        attr.text = str(self.start_at_startup)
        root.append(attr)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'SchedulableClass'
        attr.text = str(self.schedulable_class)
        root.append(attr)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'SchedulableArguments'
        attr.text = ",\n".join(self.schedulable_arguments)
        root.append(attr)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'SchedulableArgumentTypes'
        attr.text = ",\n".join(self.schedulable_argument_types)
        root.append(attr)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'InitialStartDate'
        attr.text = self.initial_start_date
        root.append(attr)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'SchedulePeriod'
        attr.text = str(self.schedule_period)
        root.append(attr)

        attr = ET.Element('attribute')
        attr.attrib['name'] = 'InitialRepetitions'
        attr.text = str(self.initial_repetitions)
        root.append(attr)
        return root
