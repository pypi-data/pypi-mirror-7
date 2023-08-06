"""Distributed execution using an IPython cluster.

Uses IPython parallel to setup a cluster and manage execution:

http://ipython.org/ipython-doc/stable/parallel/index.html

Cluster implementation from ipython-cluster-helper:

https://github.com/roryk/ipython-cluster-helper
"""
import json
import os
import zlib

import toolz as tz

from bcbio import utils
from bcbio.log import logger, get_log_dir
from bcbio.pipeline import config_utils
from bcbio.provenance import diagnostics

from cluster_helper import cluster as ipython_cluster

def create(parallel, dirs, config):
    """Create a cluster based on the provided parallel arguments.

    Returns an IPython view on the cluster, enabling processing on jobs.
    """
    profile_dir = utils.safe_makedir(os.path.join(dirs["work"], get_log_dir(config), "ipython"))
    return ipython_cluster.cluster_view(parallel["scheduler"].lower(), parallel["queue"],
                                        parallel["num_jobs"], parallel["cores_per_job"],
                                        profile=profile_dir, start_wait=parallel["timeout"],
                                        extra_params={"resources": parallel["resources"],
                                                      "mem": parallel["mem"],
                                                      "tag": parallel.get("tag"),
                                                      "run_local": parallel.get("run_local")},
                                        retries=parallel.get("retries"))

def _get_ipython_fn(fn_name, parallel):
    import_fn_name = parallel.get("wrapper", fn_name)
    return getattr(__import__("{base}.ipythontasks".format(base=parallel["module"]),
                              fromlist=["ipythontasks"]),
                   import_fn_name)

def zip_args(items, config):
    """Compress and JSON encode arguments before sending to IPython, if configured.
    """
    if tz.get_in(["algorithm", "compress_msg"], config):
        #print [len(json.dumps(x)) for x in items]
        items = [zlib.compress(json.dumps(x, separators=(',', ':')), 9) for x in items]
        #print [len(x) for x in items]
    return items

def unzip_args(args):
    """Unzip arguments if passed as compressed JSON string.

    Checks string if zlib compressed to handle zipped and unzipped cases:
    http://stackoverflow.com/questions/5322860/how-to-detect-quickly-if-a-string-is-zlib-compressed
    https://github.com/mgoldfar/ECE595-WikiTrace/blob/master/WikiTrace.py#L66
    """
    def _is_zlib_compressed(arg):
        if not arg or not isinstance(arg, basestring) or len(arg) < 2:
            return False
        cmf = ord(arg[0])
        if cmf & 0x0f != 0x08 and cmf & 0xf0 != 0x70:
            return False
        flg = ord(arg[1])
        if (cmf * 256 + flg) % 31 != 0:
            return False
        return True
    if len(args) > 0 and all(_is_zlib_compressed(arg) for arg in args):
        return [json.loads(zlib.decompress(arg)) for arg in args]
    else:
        return args

def runner(view, parallel, dirs, config):
    """Run a task on an ipython parallel cluster, allowing alternative queue types.

    view provides map-style access to an existing Ipython cluster.
    """
    def run(fn_name, items):
        out = []
        items = [x for x in items if x is not None]
        items = diagnostics.track_parallel(items, fn_name)
        fn = _get_ipython_fn(fn_name, parallel)
        logger.info("ipython: %s" % fn_name)
        if len(items) > 0:
            items = [config_utils.add_cores_to_config(x, parallel["cores_per_job"], parallel) for x in items]
            if "wrapper" in parallel:
                wrap_parallel = {k: v for k, v in parallel.items() if k in set(["fresources"])}
                items = [[fn_name] + parallel.get("wrapper_args", []) + [wrap_parallel] + list(x) for x in items]
            items = zip_args(items, config)
            for data in view.map_sync(fn, items, track=False):
                if data:
                    out.extend(unzip_args(data))
        return out
    return run
