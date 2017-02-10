import os
import xml.etree.ElementTree as ET
from Tkinter import *
import ScrolledText
import tkFileDialog
import json
import re


class Adhoc(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

    def find_info(self):
        scroll_text_adhoc.delete(0.0, END)
        if os.path.exists("vendor_cert.txt"):
            vc_info = json.load(open("vendor_cert.txt"))
        else:
            vc_info = {}
        if os.path.exists("metric_family.txt"):
            mf_info = json.load(open("metric_family.txt"))
        else:
            mf_info = {}
        path = path_entry.get()
        list_vc_input_raw = str(scroll_text_vc.get(0.0, END))
        list_vc_input = [line for line in list_vc_input_raw.split('\n') if line]
        #scroll_text_vc.delete(0.0, END)
        #scroll_text_vc.insert(INSERT, list_vc_input)
        newly_supported_raw = str(scroll_text_newly.get(0.0, END))
        newly_supported = [line for line in newly_supported_raw.split('\n') if line]
        #scroll_text_newly.delete(0.0, END)
        #scroll_text_newly.insert(INSERT, newly_supported)
        vc_folder = os.path.join(path, 'VendorCertifications/')
        mf_folder = os.path.join(path, 'MetricFamily/')
        # mm_folder = os.path.join(path, 'Publish/')
        # vp_folder = os.path.join(path, 'VendorPriorities/')
        list_vc = [vc for vc in list_vc_input if vc not in vc_info.keys()]
        if list_vc:
            extra_vc_info = self.extra_read_xml_vc(list_vc, vc_folder)
            vc_info.update(extra_vc_info)
            json.dump(vc_info, open("vendor_cert.txt", 'w'))
            extra_mf_info = self.extra_read_xml_vc(vc_info, mf_folder)
            mf_info.update(extra_mf_info)
            json.dump(mf_info, open("metric_family.txt", 'w'))
        adhoc_pre = 'LIST OF PREVIOUS SUPPORTED METRIC FAMILY AND VENDOR CERTIFICATION\n\n' + \
                    'MF: <Display Name> | <Facet Type Name>\nVC: <Display Name> | <Facet Type Name>\n'
        adhoc_new = 'LIST OF NEWLY SUPPORTED METRIC FAMILY AND VENDOR CERTIFICATION\n\n' + \
                    'MF: <Display Name> | <Facet Type Name>\nVC: <Display Name> | <Facet Type Name>\n'
        for vc_name in list_vc_input:
            vc_part = 'VC: %s | %s' % (vc_info[vc_name]['display_name'], vc_name)
            mf_part = 'MF: %s | %s' % (mf_info[vc_info[vc_name]['mf']], vc_info[vc_name]['mf'])
            part = '\n%s\n%s\n' % (mf_part, vc_part)
            if vc_name in newly_supported:
                adhoc_new += part
            else:
                adhoc_pre += part
        if newly_supported:
            full_adhoc = adhoc_pre + '\n' + adhoc_new + '\n' + 'COMMENT'
        else:
            full_adhoc = adhoc_pre + '\n' + adhoc_new + '\n' + 'COMMENT' + '\n\n' + \
                         "According to the list of metric family and vendor certification supported above, " \
                         "it seems like this device is fully certified. " \
                         "Are you able to discover the list of agents above? " \
                         "If not, then please download and deploy the latest release. " \
                         "If you already able to discover and poll the list of supported agents above, " \
                         "then please let us know what else you're requesting us to do."
        scroll_text_adhoc.insert(INSERT, full_adhoc)
        root.clipboard_append(full_adhoc)

    @staticmethod
    def extra_read_xml_vc(list_vc, vc_folder):
        vc_info = {}
        list_vc_checked = []
        for vc_file in os.listdir(vc_folder):
            if vc_file.endswith('.xml'):
                full_path = os.path.join(vc_folder, vc_file)
                with open(full_path, 'r') as vc_open:
                    tree = ET.ElementTree(ET.fromstring(vc_open.read()))
                    root_vc = tree.getroot()
                    facet_types = root_vc.findall('FacetType')
                    for facet in facet_types:
                        for vc_name in list_vc:
                            if vc_name in list_vc_checked:
                                continue
                            if facet.attrib.get('name') == vc_name:
                                list_vc_checked.append(vc_name)
                                if facet.find('DisplayName') is not None:
                                    display_name = facet.find('DisplayName').text
                                else:
                                    display_name = 'not defined'
                                expressions = facet.find('Expressions')
                                expression_group = expressions.find('ExpressionGroup')
                                mf_name = expression_group.attrib.get('destCert')
                                #mf_name = mf_name.replace('{http://im.ca.com/normalizer}', '')
                                mf_name = re.sub('\{.*\}', '', mf_name)
                                vc_info[vc_name] = {'display_name': display_name, 'mf': mf_name}

            if len(list_vc_checked) == len(list_vc):
                break
        json.dump(vc_info, open("vendor_cert.txt", 'w'))
        return vc_info

    @staticmethod
    def read_xml_vc(vc_folder):
        vc_info = {}
        for vc_file in os.listdir(vc_folder):
            if vc_file.endswith('.xml'):
                full_path = os.path.join(vc_folder, vc_file)
                with open(full_path, 'r') as vc_open:
                    tree = ET.ElementTree(ET.fromstring(vc_open.read()))
                    root_vc = tree.getroot()
                    facet_types = root_vc.findall('FacetType')
                    for facet in facet_types:
                        vc_name = facet.attrib.get('name')
                        if facet.find('DisplayName') is not None:
                            display_name = facet.find('DisplayName').text
                        else:
                            display_name = 'not defined'
                        expressions = facet.find('Expressions')
                        expression_group = expressions.find('ExpressionGroup')
                        mf_name = expression_group.attrib.get('destCert')
                        #mf_name = mf_name.replace('{http://im.ca.com/normalizer}', '')
                        mf_name = re.sub('\{.*\}', '', mf_name)
                        vc_info[vc_name] = {'display_name': display_name, 'mf': mf_name}
        json.dump(vc_info, open("vendor_cert.txt", 'w'))

    @staticmethod
    def extra_read_xml_mf(vc_info, mf_folder):
        mf_info = {}
        list_vc_checked = []
        for mf_file in os.listdir(mf_folder):
            if mf_file.endswith('.xml'):
                full_path = os.path.join(mf_folder, mf_file)
                with open(full_path, 'r') as mf_open:
                    tree = ET.ElementTree(ET.fromstring(mf_open.read()))
                    root_mf = tree.getroot()
                    facet_types = root_mf.findall('FacetType')
                    for facet in facet_types:
                        for vc_name in vc_info:
                            if vc_name in list_vc_checked:
                                continue
                            mf_name = vc_info[vc_name]['mf']
                            xml_mf_name = facet.attrib.get('name')
                            xml_mf_name = re.sub('\{.*\}', '', xml_mf_name)
                            if xml_mf_name == mf_name:
                                list_vc_checked.append(vc_name)
                                if facet.find('DisplayName') is not None:
                                    display_name = facet.find('DisplayName').text
                                else:
                                    display_name = 'not defined'
                                mf_info[mf_name] = display_name
            if len(list_vc_checked) == len(vc_info):
                break
        return mf_info

    @staticmethod
    def read_xml_mf(mf_folder):
        mf_info = {}
        for mf_file in os.listdir(mf_folder):
            if mf_file.endswith('.xml'):
                full_path = os.path.join(mf_folder, mf_file)
                with open(full_path, 'r') as mf_open:
                    tree = ET.ElementTree(ET.fromstring(mf_open.read()))
                    root_mf = tree.getroot()
                    facet_types = root_mf.findall('FacetType')
                    for facet in facet_types:
                        mf_name = facet.attrib.get('name')
                        mf_name = mf_name.replace('{http://im.ca.com/normalizer}', '')
                        if facet.find('DisplayName') is not None:
                            display_name = facet.find('DisplayName').text
                        else:
                            display_name = 'not defined'
                        mf_info[mf_name] = display_name
        json.dump(mf_info, open("metric_family.txt", 'w'))

    @staticmethod
    def clear():
        scroll_text_vc.delete(0.0, END)
        scroll_text_newly.delete(0.0, END)
        scroll_text_adhoc.delete(0.0, END)

    @staticmethod
    def get_path():
        folder_p = tkFileDialog.askdirectory(initialdir=os.path.expanduser('~/Desktop'))
        path_entry.insert(INSERT, folder_p)

    def update_data(self):
        path = path_entry.get()
        vc_folder = os.path.join(path, 'VendorCertifications/')
        mf_folder = os.path.join(path, 'MetricFamily/')
        self.read_xml_vc(vc_folder)
        self.read_xml_mf(mf_folder)

if __name__ == "__main__":
    folder = 'y:/network/snmpcollector/'
    #folder = 'd:/Dropbox/Temp/'
    root = Tk()
    root.resizable(width=False, height=False)
    root.title("Generate AdHoc")

    adhoc = Adhoc(root)

    blank_label = Label(root, text="", width=2)
    blank_label.grid(column=1, row=1)
    path_label = Label(root, text="XML:", width=5)
    path_label.grid(column=2, row=2)
    path_entry = Entry(root, width=113)
    path_entry.insert(INSERT, folder)
    path_entry.grid(column=3, row=2)
    # Browse button
    browse_button = Button(root, text="Browse", command=adhoc.get_path, width=10)
    browse_button.grid(column=5, row=2, sticky=W)

    frame_input = Frame(root, width=100)
    frame_input.grid(column=3, row=3)
    label_vc = Label(frame_input, text="RESULTS OF DISCOVERY", width=20)
    label_vc.grid(column=1, row=1)
    scroll_text_vc = ScrolledText.ScrolledText(frame_input, width=40, height=20, wrap=WORD)
    scroll_text_vc.grid(column=1, row=2)
    label_newly = Label(frame_input, text="NEWLY SUPPORTED", width=20)
    label_newly.grid(column=3, row=1)
    scroll_text_newly = ScrolledText.ScrolledText(frame_input, width=40, height=20, wrap=WORD)
    scroll_text_newly.grid(column=3, row=2)

    frame_button = Frame(root, width=100)
    frame_button.grid(column=3, row=4)
    button_check = Button(frame_button, text='   CHECK   ', command=adhoc.find_info)
    button_check.grid(column=1, row=1)
    blank_label = Label(frame_button, text="", width=5)
    blank_label.grid(column=2, row=1)
    button_clear = Button(frame_button, text='   CLEAR   ', command=adhoc.clear)
    button_clear.grid(column=3, row=1)
    blank_label = Label(frame_button, text="", width=5)
    blank_label.grid(column=4, row=1)
    button_clear = Button(frame_button, text='   UPDATE DATA   ', command=adhoc.update_data)
    button_clear.grid(column=5, row=1)

    frame_result = Frame(root, width=100)
    frame_result.grid(column=3, row=5)

    label_adhoc = Label(frame_result, text="R&D COMMENT", width=20)
    label_adhoc.grid(column=1, row=1)
    scroll_text_adhoc = ScrolledText.ScrolledText(frame_result, width=80, height=25, wrap=WORD)
    scroll_text_adhoc.grid(column=1, row=2)
    root.mainloop()
