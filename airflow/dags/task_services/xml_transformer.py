#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Authors: Maarten, Rudolf, Walter
#
#  airflow/dags/task_services/vkc_api.py
#
#   Transform xml document from vkc format into mediahaven format
#   using an xslt and saxonc library.
#   right now it resides in:
#   resources/lido_to_mam/main.xslt but might be fetched
#   using a request in the future.
#
#   for saxonc on macOS to work. run scripts/install_mac_saxon.sh and then
#   export PYTHONPATH=$(pwd)/saxon/Saxon.C.API/python-saxon
#
#   WARNING: memory leak issue in saxonc.
#   Look at task_services/transformer_process.py for a workaround/fix.
#

import os
import saxonc


class XmlTransformer:
    def __init__(self):
        """ Transforms VKC xml into MAM xml format using
            resources/XSLT_NAME/main.xslt """
        XSLT_NAME = os.environ.get('XSLT_NAME', 'lido_to_mam')
        self.xslt_path = self.__get_path_to_xslt(XSLT_NAME)
        self.saxon_processor = saxonc.PySaxonProcessor(license=False)

    def __del__(self):
        # this destructor fixes warning dialog on mac. info:
        # https://github.com/rimmartin/saxon-node/issues/21
        self.saxon_processor.release()

    def convert(self, vkc_xml):
        self.xslt_proc = self.saxon_processor.new_xslt30_processor()
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
