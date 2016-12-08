#encoding: utf-8

import zipfile
import glob
import util.crypt_util as crypt_util

def zip(paths, dest_file):
    with zipfile.ZipFile(dest_file, 'w') as zf:
        for path in paths:
            for name in glob.glob(path):
                print "zip :", name
                zf.write(name, compress_type=zipfile.ZIP_DEFLATED)
        zf.close()

def pack(paths, dst="pkg/opt"):
    zip(paths, dst+"/package.zip")

    z = open(dst+"/package.zip")
    key = crypt_util.sign(z.read())
    z.close()

if __name__ == "__main__":
    # Zipping package
    files = ["public.key", "setup.py", "gotham.py", "util/*.py", "net/*.py"]
    pack(files)
    print "[!] Finished"