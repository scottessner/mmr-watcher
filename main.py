import requests
import os
from inotify.adapters import InotifyTree
import inotify.constants as ic
import json
import re
from threading import Thread


class Watcher:

    def __init__(self, tracked_folder, include_regex, exclude_regex):
        self.tracked_folder = tracked_folder
        self.include_regex = include_regex
        self.exclude_regex = exclude_regex
        self.url = os.environ['API_URL']

    def add_file(self, path):
        folder, file = os.path.split(path)

        resp = requests.get('{}/titles/search'.format(self.url),
                            params={'path': path})

        if resp.status_code == 200:
            titles = json.loads(resp.text)
            for title in titles:

                if title['path'] == path:
                    # print('Already in system: {}'.format(path))
                    return

        resp = requests.post('{}/titles'.format(self.url),
                             json={'path': path})

        if resp.status_code == 201:
            print('Added: {}'.format(file))
        elif resp.status_code == 400:
            print('Not added: {}'.format(file))

    def watch_folder(self):

        print('Setting up watches for {}'.format(self.tracked_folder))
        i = InotifyTree(self.tracked_folder)
        print('Complete')

        for event in i.event_gen():

            if event is not None:

                (eventinfo, typenames, folder, file) = event

                print(event)

                if eventinfo.mask in [ic.IN_MOVED_TO, ic.IN_CLOSE_WRITE, ic.IN_CREATE]:

                    path = os.path.join(folder, file).encode('utf-8', 'surrogateescape').decode('utf-8')

                    if re.search(self.include_regex, path):

                        if not re.search(self.exclude_regex, path):

                            print('Adding file {}'.format(path))
                            self.add_file(path)
                            print('Complete')


if __name__ == "__main__":
    w1 = Watcher('/data/tvshows', r'\.mkv|\.mp4|\.ts\Z', r'\.grab')
    t1 = Thread(target=w1.watch_folder)
    t1.start()

    w2 = Watcher('/data/movies', r'\.mkv|\.mp4|\.ts\Z', r'\.grab')
    t2 = Thread(target=w2.watch_folder)
    t2.start()

    t1.join()
    t2.join()
