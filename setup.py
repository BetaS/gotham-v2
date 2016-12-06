#encoding; utf-8

import zipfile
import util.crypt_util as crypt_util

def unzip(source_file, dest_path):
    with zipfile.ZipFile(source_file, 'r') as zf:
        zf.extractall(path=dest_path)
        zf.close()

def unpack(paths, src="pkg/opt", dst="pkg/src"):
    f = open(src+"/package.inf", "rb")
    key = f.read()
    f.close()

    z = open(src+"/package.zip")
    v = crypt_util.verify(z.read(), key)
    z.close()

    if v:
        unzip(src+"/package.zip", dst)

        return True
    else:
        return False

if __name__ == "__main__":
    unpack()