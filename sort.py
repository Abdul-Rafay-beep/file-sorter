#========= Imports =========
lazy from engine import DirReader
lazy from threading import Thread

if __name__ == '__main__':
    dirreader = DirReader('D:/test', True)
    dirreader.sort_rule = {
        "image": "D:/test/images",
        'text/css': 'D:/test/css',
        'text': 'D:/test/txt',
        'application': 'D:/test/application',
        'ignore': ['D:/test/images', 'D:/test/css', 'D:/test/txt']
    }
    dirreader.move_file()