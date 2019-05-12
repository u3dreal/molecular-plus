
from molecular import bl_info
from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk


with ZipFile('molecular_{}_win'.format(('.'.join(map(str, bl_info['version'])))) + '.zip', 'w') as z:
    for root, _, files in walk('molecular'):
        for file in files:
            if not file.endswith('.py') and not file.endswith('.pyd'):
                continue
            z.write(path.join(root, file), compress_type=ZIP_DEFLATED)
