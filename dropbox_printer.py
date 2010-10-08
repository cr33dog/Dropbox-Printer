#!/usr/bin/env python


import os
import subprocess
import pyinotify
import cups

# path to Dropbox Folder
path = os.path.expanduser('~/Dropbox/print_queue/')

# whether or not to delete files after printing
empty_queue = True

# file extensions to run through imagemagick
ext_to_convert = ('svg')

# arguments to convert command
convert_args = ['-page','Letter']

# CUPS job options
cups_options = {}

def check(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            raise

# based on the pyinotify loop.py example
def watch (path):
    wm = pyinotify.WatchManager()
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    mask = pyinotify.ALL_EVENTS
    wm.add_watch(path, mask, rec=False) #rec=False prevents recursion
    notifier.loop()

def sendToPrinter (filename, tempname=None):
    conn = cups.Connection()
    printer = conn.getDefault()
    try:
        if tempname:
            job = conn.printFile(printer, tempname, '', cups_options)
            os.remove(tempname)
        else:
            job = conn.printFile(printer, filename, '', cups_options)
    except:
        raise
    if empty_queue:
        os.remove(filename)


class EventHandler (pyinotify.ProcessEvent):
    def process_IN_MOVED_TO(self, event):
        if event.dir == False:
            if event.name.split('.')[-1].lower() in ext_to_convert:
                tempname = '/tmp/' + event.name + '.png'
                convert_cmd = ['convert', event.pathname]
                convert_cmd.extend(convert_args)
                convert_cmd.append(tempname)
                subprocess.call(convert_cmd)
                sendToPrinter(event.pathname, tempname)
            else:
                sendToPrinter(event.pathname)

if __name__ == '__main__':
    check(path)
    watch(path)
