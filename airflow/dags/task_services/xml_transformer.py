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

        # TODO: instead do a POST /v1/transform to the deployed mtd-transformer.

        # # this code would work, but needs more setup, cython binding and saxon home edition
        # # installed with java and a whole lot of other things I'm missing in our setup...
        # xslt_path = self.__get_path_to_xslt('lido_to_mam')
        # xslt_proc = self.saxon_processor.new_xslt30_processor()
        # #node = self.saxon_processor.parse_xml(xml_text=xml.decode("utf-8"))
        # node = self.saxon_processor.parse_xml(xml_text=lido_xml)
        # result = xslt_proc.transform_to_string(stylesheet_file=xslt_path, xdm_node=node)
        # 
        # return result


    # def __get_path_to_xslt(self, transformation: str):
    #     # The xslt should exist in the resources folder.
    #     base_dir = os.getcwd()
    #     xslt_path = os.path.join(base_dir, "resources", transformation, "main.xslt")
    #     return xslt_path

