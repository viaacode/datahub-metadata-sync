from multiprocessing import Process, Queue
from task_services.xml_transformer import XmlTransformer
# wrapper around XmlTransformer. needed because currently the transformer
# does not release memory between batches. This causes memory usage to grow to gigabytes
# when converting +5000 records. By forking a new process for each batch
# memory is released and performance is still ok.


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
