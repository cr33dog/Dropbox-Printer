#!/usr/bin/env python


import os
import subprocess
import pyinotify

# path to Dropbox Folder
path = os.path.expanduser('~/Dropbox/print_queue/')

# file extensions to run through imagemagick
ext_to_convert = ('svg')

# arguments to convert command
convert_args = ['-page','Letter']


def check(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            raise

# based on the pyinotify loop.py example
def watch(path):
    wm = pyinotify.WatchManager()
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    mask = pyinotify.ALL_EVENTS
    wm.add_watch(path, mask, rec=False) #rec=False prevents recursion
    notifier.loop()

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MOVED_TO(self, event):
        if event.dir == False:
            if event.name.split('.')[-1].lower() in ext_to_convert:
                tempname = '/tmp/' + event.name + '.png'
                convert_cmd = ['convert', event.pathname]
                convert_cmd.extend(convert_args)
                convert_cmd.append(tempname)
                subprocess.call(convert_cmd)
                subprocess.call(['lpr', tempname])
                os.remove(tempname)
                os.remove(event.pathname)
            else:
                subprocess.call(['lpr', event.pathname])
                os.remove(event.pathname)

if __name__ == '__main__':
    check(path)
    watch(path)
