# encoding:utf-8

import web
import os
import qrcode
import random

urls = ('/', 'Upload')
root = os.path.dirname(__file__)
render = web.template.render(os.path.join(root, 'templates/'))


class Upload:

    def GET(self):
        web.header("Content-Type", "text/html; charset=utf-8")
        search_dir = "/Users/Flowerowl/packages/upload/"
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
        filedir = '/Users/Flowerowl/packages/upload'
        if x.myfile != "" and x.myurl == "":
            filepath = x.myfile.filename.replace('\\', '/')
            filename = filepath.split('/')[-1].strip()
            if os.path.exists(filepath):
                filename = str(random.random()*10000) + filename
            fout = open(filedir + '/' + filename, 'w')
            fout.write(x.myfile.file.read())
            fout.close()
            create_qrcode(
                'http://localhost:8001/packages/upload/' + filename, filename)
        if x.myurl != "":
            filename = x.myurl.replace('://', '_').replace('.', '_')
            create_url_file(filename)
            create_qrcode(x.myurl, filename)
        raise web.seeother('/')


def create_url_file(filename):
    filename += str(random.random() * 10000)
    f = open(filename, 'w')
    f.write(' ')
    f.close()


def create_qrcode(url, filename):
    img = qrcode.make(url)
    img.save('/Users/Flowerowl/packages/upload/qrcode/' + filename + '.jpg')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
