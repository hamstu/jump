#!/usr/bin/env python

# jump
# Makes your `cd`ing lightning fast.
#
# @author: Hamish Macpherson
# @url: https://github.com/hamstu/jump
#
# See README.md for installation and usage.

"""\
Jump makes your `cd`ing lightning fast.

Usage:
  j [OPTION]

Options:
  none                 Shows all possible paths in a numbered list for easy jumping
  X                    Jumps to path at index X
  -a [path_name]       Adds a path to the list, if no path specified it adds the present directory
  -e                   Opens the ~/.jumplist file for editing
  -h                   Shows this help information
"""

import os
import sys
import urwid
#import logging


class PathItemWidget(urwid.WidgetWrap):
    def __init__(self, idx, path, parent):
        self.id = id
        self.content = idx
        self.parent = parent
        #self.item = [
        #    ('fixed', 15, urwid.Padding(urwid.AttrWrap(
        #        urwid.Text('%s' % str(id)), 'body', 'focus'), left=2)),
        #    urwid.AttrWrap(urwid.Text('%s' % description), 'body', 'focus'),
        #]
        #self.item = urwid.AttrWrap(urwid.Text(' [%s] %s' % (str(idx), path)), 'box', 'focus')
        basename = os.path.basename(path)
        text = [('dull', ' %s ' % str(idx)), ('white', "%s - " % basename), path]
        text = urwid.Text(text)
        self.item = urwid.AttrWrap(text, 'box', 'focus')
        #w = urwid.Columns(self.item)
        self.__super.__init__(self.item)

    def selectable(self):
        return True

    def keypress(self, size, key):
        #logging.debug('itemlevel = %s' % str([size, key]))
        if key in ['down', 'up']:  # pass these to the JumperListScreen
            self.parent.keystroke(key)
        return key


class JumperListScreen:
    def __init__(self, jumper):
        self.jumper = jumper
        self.view = None
        self.listbox = None
        self.started = False
        self.items = []
        self.search = ""

        self.palette = [
            ('focus',   'dark red',     'black',    'standout',     '#fc0',     '#000'),
            ('head',    'light red',    'black',    '',             '#600',     '#f80'),
            ('foot',    'light red',    'black',    '',             'g60',      'g20'),
            ('bg',      'dark gray',    '',         '',             'g14',      '#000'),
            ('box',     '',             '',         '',             'g80',      'g15'),
            ('dull',    '',             '',         '',             'g35',      'g15'),
            ('white',    '',             '',         '',            '#fff',     'g15'), ]

        self.loadItems()

    def loadItems(self):
        for idx, p in enumerate(self.jumper.paths):
            self.items.append(PathItemWidget(idx, p, self))

    def doSearch(self):
        if self.search == "":
            self.updateHeader('')
            return
        else:
            idx = int(self.search)
            #logging.debug("Searching for " + str(idx))
            if idx < len(self.items):
                self.updateHeader('%s selected (backspace to clear)' % str(idx))
                self.listbox.set_focus(idx)
            else:
                self.updateHeader('%s not found (backspace to clear)' % str(idx))

    def updateHeader(self, title):
        if self.view:
            self.view.set_header(urwid.AttrWrap(urwid.Text(' jump %s' % str(title)), 'head'))

    def keystroke(self, input):
        #logging.debug('toplevel = %s' % str(input))
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        elif input is 'enter':
            idx = self.listbox.get_focus()[0].content
            self.jumper.run([None, str(idx)])

        elif input in ('up', 'down', 'backspace'):
            self.search = ""
            self.doSearch()

        elif str(input).isdigit():
            self.search = self.search + str(input)
            self.doSearch()

        #elif input is 'backspace':
        #    self.search = self.search[:-1]
        #    self.doSearch()

    def start(self):
        header = urwid.AttrMap(urwid.Text(' jump '), 'head')
        footer = urwid.AttrMap(urwid.Text('pwd: %s\nv1.0 | \'q\' to quit | type digits for quick select' % self.jumper.cwd), 'foot')
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(self.items))
        self.view = urwid.Frame(self.listbox, header=header, footer=footer)

        main = urwid.AttrMap(self.view, 'box')
        bg = urwid.AttrMap(urwid.SolidFill(u'/'), 'bg')
        top = urwid.Overlay(main, bg,
                            align='center', width=('relative', 90),
                            valign='middle', height=('relative', 80),
                            min_width=20, min_height=9)

        loop = urwid.MainLoop(top, self.palette, unhandled_input=self.keystroke)
        loop.screen.set_terminal_properties(colors=256)
        self.started = True
        loop.run()

    def close(self):
        if self.started:
            raise urwid.ExitMainLoop()


class Jumper():
    def __init__(self):
        self.home_path = os.path.expanduser("~")
        self.paths = []
        self.cwd = os.getcwd()

        self.loadPaths()
        self.screen = JumperListScreen(self)

    def printHelp(self):
        print (__doc__)

    def jumpTo(self, path):
        jumpfile = open(os.path.join(self.home_path, ".jumpfile"), "w")
        jumpfile.write(path)
        jumpfile.close()

        self.screen.close()
        sys.exit()

    def run(self, arguments):
        """Start the program and runs a command based on the arguments"""
        if len(arguments) > 1:
            command = arguments[1]

            # --------------
            # Add a new path
            # --------------
            if command in ["-add", "-a"]:
                if len(arguments) > 2:
                    newpath = arguments[2]
                    self.paths.append(newpath)
                    self.savePaths()
                    print self.paths
                else:
                    self.paths.append(self.cwd)
                    self.savePaths()
            elif command in ["-help", "-h", "?"]:
                self.printHelp()
            elif command == "-edit" or command == "-e":
                os.system('"${EDITOR:-vi}" %s' % os.path.join(self.home_path, ".jumplist"))
            elif command.isdigit():
                index = int(command)
                if index < len(self.paths):
                    self.jumpTo(self.paths[index])
                else:
                    pass
            else:
                print 'Unrecognized option `%s`' % command
                self.printHelp()

        else:
            # Start our listing screen
            self.screen.start()

    def savePaths(self):
        jumplist = os.path.join(self.home_path, ".jumplist")
        jumplist = open(jumplist, "w")
        for item in self.paths:
            jumplist.write("%s\n" % item)

    def loadPaths(self):
        jumplist = os.path.join(self.home_path, ".jumplist")
        jumplist = open(jumplist, "r").readlines()
        self.paths = [x.strip() for x in jumplist]


if __name__ == '__main__':
    #logging.basicConfig(filename='jump.log', level=logging.ERROR)
    #logging.debug('Starting jump...')
    jumper = Jumper()
    jumper.run(sys.argv)
