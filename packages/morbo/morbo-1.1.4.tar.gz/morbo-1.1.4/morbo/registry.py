import weakref
import threading
from functools import partial

_local = threading.local()
_local.instances = {}

models = {}
back_references = {}


def clear():
    global models, back_references, _local
    models = {}
    back_references = {}
    _local = threading.local()
    _local.instances = {}
    
    
def add_model_instance(inst):
    id = unicode(inst._id)
    callback = partial(_remove_model_inst_ref, id)
    ref = weakref.ref(inst, callback)
    if id not in _local.instances:
        _local.instances[id] = [ref]
    else:
        _local.instances[id].append(ref)
    
    
def _remove_model_inst_ref(id, r):
    refs = _local.instances.get(id)
    if refs:
        try:
            refs.remove(r)
        except ValueError:
            pass
        if len(refs) == 0:
            _local.instances.pop(id)
    
    
def get_model_instances(id):
    id = unicode(id)
    refs = _local.instances.get(id, [])
    insts = []
    for r in refs:
        inst = r()
        if inst:
            insts.append(inst)
    return insts
    