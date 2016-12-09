#encoding: utf-8

import zipfile
import glob
import util.update_util as update_util
import util.crypt_util as crypt_util
import os

def zip(paths, dest_file):
    with zipfile.ZipFile(dest_file, 'w') as zf:
        for path in paths:
            for name in glob.glob(path):
                print "zip :", name
                zf.write(name, compress_type=zipfile.ZIP_DEFLATED)
        zf.close()

def pack(paths, dst="pkg/opt", name="package"):
    zip(paths, dst+"/"+name+".zip")

    z = open(dst+"/"+name+".zip")
    key = crypt_util.sign(z.read())
    z.close()

if __name__ == "__main__":
    # Zipping package
    print "[!] Start"

    os.chdir("pkg/src/httpd")
    files = ["public.key", "httpd.py", "res/*"]
    pack(files, "../../dist", "httpd")
    data = update_util.get_metadata("../../dist/httpd.zip")

    f = open("../../dist/httpd.key", "wb")
    f.write(data)
    f.close()

    os.chdir("../monitor")
    files = ["public.key", "monitor.py"]
    pack(files, "../../dist", "monitor")

    data = update_util.get_metadata("../../dist/monitor.zip")

    f = open("../../dist/monitor.key", "wb")
    f.write(data)
    f.close()

    print "[!] Finished"