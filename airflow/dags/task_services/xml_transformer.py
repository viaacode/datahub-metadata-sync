#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
# import saxonc
# from pathlib import Path
# from typing import List

class XmlTransformer:
    def __init__(self):
        """transform OAI into MAM xml format"""
        print("XmlTransformer initialized")


    def convert(self, lido_xml):
        return 'TODO CONVERT TO MAM FORMAT:' + lido_xml

        # TODO: in meeting tomorrow we might 
        # do a POST /v1/transform to the deployed mtd-transformer.
        # or somehow fetch the lido_to_mam xlst from the mtd-transformer and then
        # run below code. (Needs some setup of Saxon HE to be installed, see Dockerfile
        # for inspiration...

        # xslt_path = self.__get_path_to_xslt('lido_to_mam')
        # xslt_proc = self.saxon_processor.new_xslt30_processor()
        # # node = self.saxon_processor.parse_xml(xml_text=xml.decode("utf-8"))
        # node = self.saxon_processor.parse_xml(xml_text=lido_xml)
        # result = xslt_proc.transform_to_string(stylesheet_file=xslt_path, xdm_node=node)
        # 
        # return result


    # def __get_path_to_xslt(self, transformation: str):
    #     # The xslt should exist in the resources folder.
    #     base_dir = os.getcwd()
    #     xslt_path = os.path.join(base_dir, "resources", transformation, "main.xslt")
    #     return xslt_path

