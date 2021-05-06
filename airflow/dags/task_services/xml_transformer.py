#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import saxonc

# for saxonc on mac to work. run scripts/install_mac_saxon.sh and then
# export PYTHONPATH=$(pwd)/saxon/Saxon.C.API/python-saxon


class XmlTransformer:
    def __init__(self):
        """ Transforms VKC xml into MAM xml format using
            resources/lido_to_mam/main.xslt """
        self.saxon_processor = saxonc.PySaxonProcessor(license=False)
        self.xslt_path = self.__get_path_to_xslt('lido_to_mam')
        self.xslt_proc = self.saxon_processor.new_xslt30_processor()
        print("XmlTransformer initialized")

    def __del__(self):
        # fixes warning dialog on mac:
        # https://github.com/rimmartin/saxon-node/issues/21
        self.saxon_processor.release()

    def convert(self, vkc_xml):
        vkc_root = self.saxon_processor.parse_xml(xml_text=vkc_xml)
        return self.xslt_proc.transform_to_string(
            stylesheet_file=self.xslt_path,
            xdm_node=vkc_root
        )

    def __get_path_to_xslt(self, transformation: str):
        # The xslt should exist in the resources folder.
        base_dir = os.getcwd()
        xslt_path = os.path.join(
            base_dir, "airflow", "dags", "resources",
            transformation, "main.xslt"
        )
        return xslt_path
