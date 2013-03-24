#!/usr/bin/env python

######################################################
#
# jump
# Makes your `cd`ing fast and fun.
#
# @author: Hamish Macpherson
# @url: https://github.com/hamstu/jump
#
# See README.md for installation and usage.
#
######################################################

"""\
Jump makes your `cd`ing fast and fun.

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


class PathItemWidget(urwid.WidgetWrap):
    def __init__(self, idx, path, colwidth, parent):
        self.id = id
        self.content = idx
        self.parent = parent

        basename = os.path.basename(path)
        text = [('dull', ' %s  ' % str(idx)), ('white', "%s" % basename.ljust(colwidth, " ")), path]
        text = urwid.Text(text)

        self.item = urwid.AttrWrap(text, 'box', 'focus')
        self.__super.__init__(self.item)

    def selectable(self):
        return True

    def keypress(self, size, key):
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
            ('foot',    'light red',    'black',    '',             'g60',      'g15'),
            ('bg',      'dark gray',    '',         '',             'g14',      '#000'),
            ('box',     '',             '',         '',             'g80',      'g9'),
            ('dull',    '',             '',         '',             'g35',      'g9'),
            ('white',    '',             '',         '',            '#fff',     'g9'), ]

        self.loadItems()

    def loadItems(self):
        colwidth = max([len(os.path.basename(x)) for x in self.jumper.paths]) + 2
        for idx, p in enumerate(self.jumper.paths):
            self.items.append(PathItemWidget(idx, p, colwidth, self))

    def doSearch(self):
        maxdigits = len(str(len(self.items)))
        if self.search == "":
            self.updateHeader('')
            return
        else:
            if len(self.search) > maxdigits:
                self.search = self.search[-1:]

            idx = int(self.search)
            if idx < len(self.items):
                self.updateHeader('%s selected (backspace to clear)' % str(idx))
                self.listbox.set_focus(idx)
            else:
                self.updateHeader('%s not found (backspace to clear)' % str(idx))
                self.listbox.set_focus(len(self.items)-1)

    def updateHeader(self, title):
        if self.view:
            self.view.set_header(urwid.AttrWrap(urwid.Text(' jump %s' % str(title), align='center'), 'head'))

    def keystroke(self, input):
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

    def start(self):
        header = urwid.AttrMap(urwid.Text(' jump ', align='center'), 'head')
        footer = urwid.AttrMap(urwid.Text(' pwd: %s\n v1.0 | \'q\' to quit | type digits for quick select' % self.jumper.cwd), 'foot')
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
        """Runs a jump command based on the arguments"""
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
                else:
                    self.paths.append(self.cwd)
                    self.savePaths()

            # --------------
            # Show help
            # --------------
            elif command in ["-help", "-h", "?"]:
                self.printHelp()

            # --------------
            # Edit paths
            # --------------
            elif command in ["-edit", "-e"]:
                os.system('"${EDITOR:-vi}" %s' % os.path.join(self.home_path, ".jumplist"))

            # --------------
            # Jump to index
            # --------------
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
        try:
            jumplist = open(jumplist, "r").readlines()
            self.paths = [x.strip() for x in jumplist]
        except IOError:
            # File not found? Let's fill in a default
            self.paths = [self.home_path]


if __name__ == '__main__':
    jumper = Jumper()
    jumper.run(sys.argv)
