#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import saxonc
from pathlib import Path
# from typing import List

# for saxonc on mac to work. run scripts/install_mac_saxon.sh and then
# also do this:
# export PYTHONPATH=$(pwd)/saxon/Saxon.C.API/python-saxon

class XmlTransformer:
    def __init__(self):
        """transforms VKC xml into MAM xml format using resources/lido_to_mam/main.xslt"""
        self.saxon_processor = saxonc.PySaxonProcessor(license=False)
        print("XmlTransformer initialized")
        # https://github.com/rimmartin/saxon-node/issues/21
        # should release this in the end, self.saxon_processor.release()


    def convert(self, lido_xml):
        # return 'TODO CONVERT TO MAM FORMAT:' + lido_xml
        xslt_path = self.__get_path_to_xslt('lido_to_mam')
        xslt_proc = self.saxon_processor.new_xslt30_processor()
        # node = self.saxon_processor.parse_xml(xml_text=xml.decode("utf-8"))
        node = self.saxon_processor.parse_xml(xml_text=lido_xml)
        result = xslt_proc.transform_to_string(stylesheet_file=xslt_path, xdm_node=node)
        
        return result


    def __get_path_to_xslt(self, transformation: str):
        # The xslt should exist in the resources folder.
        base_dir = os.getcwd()
        xslt_path = os.path.join(base_dir, "airflow", "dags", "resources", transformation, "main.xslt")
        return xslt_path

