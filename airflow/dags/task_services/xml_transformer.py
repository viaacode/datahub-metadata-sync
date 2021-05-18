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
#   memory leak issue here, its explained here : https://saxonica.plan.io/issues/4942
#   aha and I see Rudolf also shows this on an example https://github.com/RudolfDG/saxon-flask-api
#   and asks about the same issue on stackoverflow ;)
#   https://stackoverflow.com/questions/66693687/how-to-prevent-saxon-c-python-bindings-from-trying-to-start-a-new-java-vm-when-a
import os
import saxonc


class XmlTransformer:
    def __init__(self):
        """ Transforms VKC xml into MAM xml format using
            resources/XSLT_NAME/main.xslt """
        XSLT_NAME = os.environ.get('XSLT_NAME', 'lido_to_mam')
        self.xslt_path = self.__get_path_to_xslt(XSLT_NAME)
        self.saxon_processor = saxonc.PySaxonProcessor(license=False)
        print("XmlTransformer initialized")

    def __del__(self):
        # this destructor fixes warning dialog on mac. info:
        # https://github.com/rimmartin/saxon-node/issues/21
        self.saxon_processor.release()

    # try re-creating and releasing processor between batches to solve memleak
    # this doesnt work though, memory growth issue remains:
    # import gc
    # import time
    # def release_processor_memory(self):
    #     self.saxon_processor.__exit__()
    #     self.saxon_processor = saxonc.PySaxonProcessor(license=False)
    #     self.xslt_proc = self.saxon_processor.new_xslt30_processor()
    #     gc.collect()
    #     time.sleep(0.1)

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
