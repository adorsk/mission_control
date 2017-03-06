import json
import io
import tarfile

def upload_action_handler(storage_client, *args, params=None, ctx=None,
                           **kwargs):
    dir_path = ctx.transform_value(params['src'])
    tgz_bytes = dir_to_tgz_bytes(dir_path=dir_path)
    storage_meta = storage_client.post_data(data=tgz_bytes)
    serialized_storage_meta = json.dumps(storage_meta)
    return serialized_storage_meta

def dir_to_tgz_bytes(dir_path=None):
    mem_file = io.BytesIO()
    tgz = tarfile.open(mode='w:gz', fileobj=mem_file)
    tgz.add(dir_path, arcname='.')
    tgz.close()
    return mem_file.getvalue()

def download_action_handler(storage_client, *args, params=None, ctx=None,
                           **kwargs):
    serialized_storage_meta = ctx.transform_value(params['storage_meta'])
    storage_meta = json.loads(serialized_storage_meta)
    src_params = storage_meta['params']
    transformed_dest = ctx.transform_value(params['dest'])
    tgz_bytes = storage_client.get_data(storage_params=src_params)
    tgz_bytes_to_dir(tgz_bytes=tgz_bytes, dir_path=transformed_dest)
    return transformed_dest

def tgz_bytes_to_dir(tgz_bytes=None, dir_path=None):
    mem_file = io.BytesIO(tgz_bytes)
    tgz = tarfile.open(mode='r:gz', fileobj=mem_file)
    tgz.extractall(path=dir_path)