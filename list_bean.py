#!/usr/bin/python3.6

import lxml.etree as ET
import re

number_pattern = r'[0-9]+'

class ListMBeans():
    def __init__(self, path='scheduler-service.xml'):
        self.mbeans = list()
        self.commented_mbeans = list()
        self.path = path
        try:
            self.etree = ET.parse(path)
        except OSError:
            print("Not found file %s" % path)
            exit(1)

    def parse(self):
        root = self.etree.getroot()
        self.mbeans.clear()
        self.commented_mbeans.clear()
        str_file = str(ET.tostring(root))
        comments = re.compile('<!--.*-->').findall(str_file)
        comments = str(comments[0]). \
            replace("<!--", "<server>"). \
            replace("-->", "</server>"). \
            replace("\\n", ""). \
            strip()
        commented = ET.fromstring(comments)
        for item in root.iter('mbean'):
            self.mbeans.append(item)
        for item in commented.iter('mbean'):
            self.commented_mbeans.append(item)

    def print(self):
        print('Enable')
        print('====================')
        for num, active in enumerate(self.mbeans):
            print(num, self.get_class_mbean(active))
        print('\nDisable')
        print('====================')
        for num, active in enumerate(self.commented_mbeans):
            print(num, self.get_class_mbean(active))
        return self.mbeans, self.commented_mbeans

    def save(self):
        start = '<?xml version="1.0" encoding="UTF-8"?>\n<server>\n<classpath codebase="." ' \
                'archives="mbean_timer.jar"/>\n '
        end = '\n</server>'
        text = start + \
               " ".join(ET.tostring(f).decode().replace('\\n', '\n') for f in self.mbeans) + \
               '<!--\n' + \
               " ".join(ET.tostring(f).decode().replace('\\n', '\n') for f in self.commented_mbeans) + \
               '\n-->' + \
               end
        element = ET.fromstring(bytes(text, 'UTF-8'))
        with open(file=self.path, mode='w+') as file:
            file.write(ET.tostring(element, pretty_print=True).decode())
            file.flush()
            file.close()

    def disable(self, names: list):
        self.parse()
        for name in names:
            bean = self.mbean_by_name(name)
            find = None
            for position, mbean in enumerate(self.mbeans):
                if re.compile(number_pattern).match(name):
                    if int(position) == int(name):
                        find = mbean
                        break
                else:
                    if bean(mbean) is not None:
                        find = mbean
                        break
            if find is not None:
                self.commented_mbeans.append(find)
                self.mbeans.remove(find)
                self.save()

    def enable(self, names: list):
        self.parse()
        for name in names:
            bean = self.mbean_by_name(name)
            find = None
            for position, mbean in enumerate(self.commented_mbeans):
                if re.compile(number_pattern).match(name):
                    if int(position) == int(name):
                        find = mbean
                        break
                else:
                    if bean(mbean) is not None:
                        find = mbean
                        break
            if find is not None:
                self.mbeans.append(find)
                self.commented_mbeans.remove(find)
                self.save()

    def mbean_by_name(self, name):
        return lambda m: m if self.get_class_mbean(m).lower().strip() == name.lower().strip() else None

    def get_class_mbean(self, active: ET.Element) -> str:
        return active.get('name').split(',')[1].replace('schedule=', '')

    def update(self, name, arg, value):
        self.parse()
        bean = self.mbean_by_name(name)
        find = None
        for mbean in self.mbeans:
            if bean(mbean) is not None:
                find = mbean
                break
        if find is not None:
            if arg == 'name':
                old_value = find.get(arg)
                old_value_arr = old_value.split('=')
                old_value_arr[len(old_value_arr) - 1] = value
                find.attrib[arg] = "=".join(old_value_arr)
            elif arg == 'event':
                change_value_in_list(find, 'SchedulableArguments', value, 2)
            elif arg == 'args':
                change_value_in_list(find, 'SchedulableArguments', value, 1)
            else:
                for attr in find.iter('attribute'):
                    if str(attr.get('name')).lower().strip() == str(arg).lower().strip():
                        attr.text = value
                        break
            self.save()

    def find(self, name: str):
        self.parse()
        find = None
        is_active = 'Active'
        for bean in self.mbeans:
            name_arr = bean.attrib['name'].split('=')
            if str(name_arr[len(name_arr) - 1]).lower().strip() == name.lower().strip():
                find = bean
                break
        if find is None:
            for bean in self.commented_mbeans:
                name_arr = bean.attrib['name'].split('=')
                if str(name_arr[len(name_arr) - 1]).lower().strip() == name.lower().strip():
                    find = bean
                    is_active = 'Commented'
                    break
        return is_active, find


def change_value_in_list(find, arg, value, postion):
    for attr in find.iter('attribute'):
        if str(attr.get('name')).lower().strip() == str(arg).lower().strip():
            old_value = attr.text
            old_value_arr = old_value.split(',')
            old_value_arr[len(old_value_arr) - postion] = '\n' + value
            attr.text = ",".join(old_value_arr)
            break
