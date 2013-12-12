# encoding:utf-8

import web
import os
import qrcode
import random
import tarfile
import zipfile

urls = ('/', 'Upload',
        '/del/(.*?)', 'Delete',
        )
root = os.path.dirname(__file__)
render = web.template.render(os.path.join(root, 'templates/'))
fileroot = root + '/static/upload/'
qrroot = root + '/static/qrcode/'
tarroot = root + '/static/tar/'


class Upload:

    def GET(self):
        web.header("Content-Type", "text/html; charset=utf-8")
        search_dir = fileroot
        os.chdir(search_dir)
        filelist = filter(os.path.isfile, os.listdir(search_dir))
        filelist = [os.path.join(search_dir, f)
                    for f in filelist]
        filelist.sort(key=lambda x: os.path.getmtime(x))
        filelist.reverse()
        filelist = [file.split('/')[-1] for file in filelist]
        return render.index(filelist)

    def POST(self):
        x = web.input(myfile={})
        filedir = fileroot

        # 如果只上传单一文件
        if x.myfile != "" and x.myurl == "":
            filepath = x.myfile.filename.replace('\\', '/')
            filename = filepath.split('/')[-1].strip()
            # 如果上传文件是文件夹的.tar.gz/.zip类型，则解压xxx.tar.gz/.zip
            tail = os.path.splitext(filepath)[-1]
            if tail == '.gz':
                newfilename = create_file(
                    filename, filepath, x.myfile.file.read())
                extract_tar_file(newfilename)
            if tail == '.zip':
                newfilename = create_file(
                    filename, filepath, x.myfile.file.read())
                extract_zip_file(newfilename)
            else:
                create_file(filename, filepath, x.myfile.file.read())
            create_qrcode(
                'http://baid.comn' + filename, filename)
        # 如果URL不为空则忽略单一文件
        if x.myurl != "":
            filename = x.myurl.replace('://', '_').replace('.', '_')
            create_url_file(filename)
            create_qrcode(x.myurl, filename)
        raise web.seeother('/')


class Delete:

    """删除文件,删除对应二维码文件"""

    def GET(self, name):
        targetFile = fileroot + name
        targetQr = qrroot + name + '.jpg'
        targetTar = tarroot + name.split('.')[0]
        if os.path.isfile(targetFile):
            os.remove(targetFile)
        if os.path.isfile(targetQr):
            os.remove(targetQr)
        if os.path.exists(targetTar):
            delete_dir_file(targetTar)
            os.rmdir(targetTar)
        raise web.seeother('/')


def delete_dir_file(dirpath):
    for root, dirs, files in os.walk(dirpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def extract_zip_file(filename):
    """解压缩zip文件,并讲文件放到static/tar/filename下"""
    path = tarroot + filename.split('.')[0]
    if not os.path.exists(path):
        os.mkdir(path)
    tfile = fileroot + filename
    with zipfile.ZipFile(tfile, 'r') as myzip:
        myzip.extractall(tarroot)

def extract_tar_file(filename):
    """解压缩tar.gz文件,并将文件放到static/tar/filename下"""
    path = tarroot + filename.split('.')[0]
    if not os.path.exists(path):
        os.mkdir(path)
    tfile = fileroot + filename
    tar = tarfile.open(tfile)
    names = tar.getnames()
    for name in names:
        tar.extract(name, path=tarroot)
    tar.close()


def create_file(filename, filepath, filecontent):
    """创建新文件"""
    filedir = fileroot
    fout = open(filedir + '/' + filename, 'w')
    fout.write(filecontent)
    fout.close()
    return filename


def create_url_file(filename):
    """创建URL物理文件"""
    f = open(fileroot + filename, 'w')
    f.write(' ')
    f.close()


def create_qrcode(url, filename):
    """创建文件链接二维码"""
    img = qrcode.make(url)
    img.save(qrroot + filename + '.jpg')


app = web.application(urls, globals())
application = app.wsgifunc()
#app.run()
