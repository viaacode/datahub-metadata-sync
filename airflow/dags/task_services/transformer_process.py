#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  @Author: Walter Schreppers
#
#  airflow/dags/task_services/transformer_process.py
#
#   Wrapper around XmlTransformer. Needed because currently the transformer
#   does not release memory between batches.
#   This causes memory usage to grow to gigabytes when converting 7000 records.
#   By forking a new process for each batch memory is released.
#
#   Issues are more explained here:
#   https://saxonica.plan.io/issues/4942
#
#   Rudolf also shows this on an example
#     https://github.com/RudolfDG/saxon-flask-api
#     and asks about the same issue on stackoverflow
# https://stackoverflow.com/questions/66693687/how-to-prevent-saxon-c-python-bindings-from-trying-to-start-a-new-java-vm-when-a
#
from multiprocessing import Process, Queue
from task_services.xml_transformer import XmlTransformer


def xml_transformer_process(vkc_xml_batch, q):
    tr = XmlTransformer()

    mam_xml_batch = []
    for vkc_xml in vkc_xml_batch:
        mam_xml = tr.convert(vkc_xml)
        mam_xml_batch.append(mam_xml)

    q.put(mam_xml_batch)


def xml_convert(vkc_xml_batch):
    q = Queue()
    p = Process(target=xml_transformer_process, args=(vkc_xml_batch, q))
    p.start()
    mam_xml_batch = q.get()
    p.join()

    return mam_xml_batch
