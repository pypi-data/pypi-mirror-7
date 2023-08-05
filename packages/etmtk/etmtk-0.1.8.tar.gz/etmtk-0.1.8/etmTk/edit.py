#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import platform, sys
import codecs
from datetime import datetime, timedelta, time

from copy import deepcopy
# from view import AFTER

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT, Listbox
    from tkinter import ttk
    # from ttk import Button, Style
    from tkinter import font as tkFont
    # from tkinter import simpledialog as tkSimpleDialog
    # from tkinter.simpledialog import askstring
    # from tkinter.messagebox import askokcancel
    from tkinter.filedialog import asksaveasfilename
    from tkinter.filedialog import askopenfilename
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT, Listbox
    import ttk
    # from ttk import Button, Style
    import tkFont
    # import tkSimpleDialog
    # from tkSimpleDialog import askstring
    from tkFileDialog import asksaveasfilename
    from tkFileDialog import askopenfilename
    from tkMessageBox import askokcancel

# Also from messagebox:
# askquestion()
# askokcancel()
# askyesno ()
# askretrycancel ()

import string
ID_CHARS = string.ascii_letters + string.digits + "_@/"

import gettext
_ = gettext.gettext

import logging
import logging.config
logger = logging.getLogger()


SOMEREPS = _('Selected repetitions')
ALLREPS = _('Repetitions')
MESSAGES = _('Error messages')
FOUND = "found"  # for found text marking

MAKE = _("Make")
PRINT = _("Print")
EXPORTTEXT = _("Export report in text format ...")
EXPORTCSV = _("Export report in CSV format ...")
SAVESPECS = _("Save changes to report specifications")
CLOSE = _("Close")


from etmTk.data import hsh2str, str2hsh, get_reps, rrulefmt, ensureMonthly, commandShortcut, optionShortcut, CMD, relpath, completion_regex, getReportData, tree2Text, AFTER, get_current_time

from etmTk.dialog import BGCOLOR, OptionsDialog, ReadOnlyText

class ReportWindow(Toplevel):
    def __init__(self, parent=None, options=None, title=None):
        Toplevel.__init__(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.configure(background=BGCOLOR)
        self.minsize(400, 300)
        self.geometry('500x200')
        self.transient(parent)
        self.parent = parent
        self.loop = parent.loop
        # self.changed = False
        self.options = options
        self.modified = False
        self.tkfixedfont = tkFont.nametofont("TkFixedFont")
        self.tkfixedfont.configure(size=self.options['fontsize_fixed'])
        # self.text_value.trace_variable("w", self.setSaveStatus)
        btnwdth = 5
        topbar = Frame(self, bd=0, relief=FLAT)
        PADY = 2
        topbar.pack(side="top", fill=X, padx=0, pady=4)
        topbar.configure(background=BGCOLOR)

        botbar = Frame(self, bd=0, relief=FLAT, highlightbackground=BGCOLOR, background=BGCOLOR)
        botbar.pack(side="bottom", fill=X, padx=0, pady=4)

        text = ReadOnlyText(self, bd=2, relief="sunken", padx=3, pady=2, font=self.tkfixedfont, width=70, takefocus=False)
        text.configure(highlightthickness=0)
        text.tag_configure(FOUND, background="lightskyblue")

        text.pack(side="top", padx=4, pady=0, expand=1, fill=BOTH)
        self.text = text

        # botbar.configure(background=BGCOLOR)

        # topbar components
        # report menu
        self.reportLabel = _("Report Commands")
        self.rm_options = [[MAKE, 'm'],
                           [EXPORTTEXT, 't'],
                           [EXPORTCSV, 'x'],
                           [SAVESPECS, 'w'],
                           [CLOSE, 'q'],
        ]

        self.rm2cmd = {'m': self.makeReport,
                         't': self.exportText,
                         'x': self.exportCSV,
                         'w': self.saveSpecs,
                         'q': self.quit}
        self.rm_opts = [x[0] for x in self.rm_options]
        self.report = self.rm_options[0][0]
        self.reportValue = StringVar(self)
        self.currentReport = StringVar(self)
        self.currentReport.set(self.report)
        self.reportValue.set(self.reportLabel)
        self.rm = OptionMenu(topbar, self.reportValue, *self.rm_opts)
        self.rm.configure(pady=2)


        for i in range(len(self.rm_options)):
            label = self.rm_options[i][0]
            k = self.rm_options[i][1]
            if i == 0:
                l = "Return"
                c = "<Return>"
            else:
                l, c = commandShortcut(k)
                logger.debug("k: {0}; l: {1}; c: {2}".format(k, l, c))
                self.bind(c, lambda e, x=k: self.after(AFTER, self.rm2cmd[x]))
            self.rm["menu"].entryconfig(i, accelerator=l, command=lambda x=k: self.after(AFTER, self.rm2cmd[x]))
        self.rm.pack(side="left", padx=2)
        self.rm.configure(background=BGCOLOR, takefocus=False)

        # find group
        Button(topbar, text='x', command=self.clearFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)
        self.find_text = StringVar(topbar)
        self.e = Entry(topbar, textvariable=self.find_text, width=10, highlightbackground=BGCOLOR)
        self.e.pack(side=LEFT, padx=0, expand=1, fill=X)
        self.e.bind("<Return>", self.onFind)
        Button(topbar, text='>', command=self.onFind, highlightbackground=BGCOLOR,  padx=8, pady=2).pack(side=LEFT, padx=0)
        Button(topbar, text=_("Quit"), command=self.quit, highlightbackground=BGCOLOR,  padx=8, pady=2).pack(side=RIGHT, padx=0)

        # # help
        # Button(topbar, text="?", command=self.reportHelp, highlightbackground=BGCOLOR).pack(side=LEFT, padx=4)

        # botbar components
        # Button(botbar, text=CLOSE, highlightbackground=BGCOLOR, width=btnwdth, command=self.cancel).pack(side=LEFT, padx=4)
        # # self.bind("<Escape>", self.quit)
        # self.bind("<Escape>", self.cancel)
        #
        # # ok will check, save and quit
        # Button(botbar, text=_("Process"), highlightbackground=BGCOLOR, width=btnwdth, command=self.makeReport).pack(side=RIGHT, padx=4)

        # reportspec

        self.box_value = StringVar()
        self.box = ttk.Combobox(botbar, textvariable=self.box_value, font=self.tkfixedfont)
        self.box.bind("<<ComboboxSelected>>", self.newselection)
        self.bind("<Return>", self.makeReport)
        self.bind("<Escape>", self.quit)
        self.bind("<Control-q>", self.quit)
        self.specs = ['']
        if ('report_specifications' in self.options and os.path.isfile(self.options['report_specifications'])):
            rf = self.options['report_specifications']
            logger.info('Using report specifications file: {0}'.format(rf))

            with open(rf) as fo:
                tmp = fo.readlines()
            self.specs = [str(x).rstrip() for x in tmp if x.strip() and x[0] != "#"]
        logger.debug('specs: {0}'.format(self.specs))
        self.value_of_combo = self.specs[0]
        self.box['values'] = self.specs
        self.box.current(0)
        self.box.configure(width=30, background=BGCOLOR, takefocus=False)
        self.box.pack(side="left", padx=2, fill=X, expand=1)
        self.box.focus_set()


    def clearFind(self, *args):
        self.text.tag_remove(FOUND, "0.0", END)
        self.find_text.set("")

    def onFind(self, *args):
        target = self.find_text.get()
        logger.debug('target: {0}'.format(target))
        if target:
            where = self.text.search(target, INSERT, nocase=1)
        if where:
            pastit = where + ('+%dc' % len(target))
            # self.text.tag_remove(SEL, '1.0', END)
            self.text.tag_add(FOUND, where, pastit)
            self.text.mark_set(INSERT, pastit)
            self.text.see(INSERT)
            self.text.focus()

    def cancel(self, e=None):
        t = self.find_text.get()
        if t.strip():
            self.clearFind()
            return "break"
        logger.debug(('calling quit'))
        self.quit()

    def saveSpecs(self, e=None):
        if not self.modified:
            return
        if not ('report_specifications' in self.options and os.path.isfile(self.options['report_specifications'])):
            return
        ans = self.confirm(parent=self,
            prompt=_("Save the changes to your report specifications?"))
        if ans:
            self.specs.sort()
            file = self.options['report_specifications']
            with open(file, 'w') as fo:
                tmp = fo.write("\n".join(self.specs))
            self.modified = False
            changed = SimpleEditor(parent=self, file=file, options=self.options, title='report_specifications').changed
            if changed:
                logger.debug("saved: {0}".format(file))
            self.box['values'] = self.specs

    def quit(self, e=None):
        if self.modified:
            self.saveSpecs()
        if self.parent:
            logger.debug('focus set')
            self.parent.focus()
            self.parent.tree.focus_set()
        self.destroy()
        return "break"

    def messageWindow(self, title, prompt):
        win = Toplevel()
        win.title(title)
        tkfixedfont = tkFont.nametofont("TkFixedFont")
        tkfixedfont.configure(size=self.options['fontsize_fixed'])
        # win.minsize(444, 430)
        # win.minsize(450, 450)
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active')
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(
            f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            # font=tkFont.Font(family="Lucida Sans Typewriter"),
            font=self.tkfixedfont,
            height=14,
            width=52,
            takefocus=False)
        t.insert("0.0", prompt)
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview, width=8)
        ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
        # t.configure(state="disabled", yscroll=ysb.set)
        t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)

        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)


    def makeReport(self, event=None):
        self.value_of_combo = self.box.get()
        if not self.value_of_combo.strip():
            return
        try:
            self.all_text = text = getReportData(
                self.value_of_combo,
                self.loop.file2uuids,
                self.loop.uuid2hash,
                self.loop.options)
            if not self.all_text:
                text = _("Report contains no output.")
            if self.value_of_combo not in self.specs:
                self.specs.append(self.value_of_combo)
                self.specs.sort()
                self.specs = [x for x in self.specs if x]
                self.box["values"] = self.specs
                self.modified = True
            logger.debug("spec: {0}".format(self.value_of_combo))
        except:
            self.all_text = text = _("'{0}' could not be processed".format(self.value_of_combo))
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)
        self.text.mark_set(INSERT, '1.0')

    def newselection(self, event=None):
        self.value_of_combo = self.box.get()

    def exportText(self):
        logger.debug("spec: {0}".format(self.value_of_combo))
        fileops = {'defaultextension': '.text',
                   'filetypes': [('text files', '.text')],
                   'initialdir': self.options['etmdir'],
                   'title': 'Text report files',
                   'parent': self}
        filename = asksaveasfilename(**fileops)
        if not filename:
            return False
        self.text = text = getReportData(
            self.value_of_combo,
            self.loop.file2uuids,
            self.loop.uuid2hash,
            self.loop.options,
            export=False)
        fo = codecs.open(filename, 'w', self.options['encoding']['file'])
        fo.write(self.text)
        fo.close()

    def exportCSV(self):
        logger.debug("spec: {0}".format(self.value_of_combo))
        data = getReportData(
            self.value_of_combo,
            self.loop.file2uuids,
            self.loop.uuid2hash,
            self.loop.options,
            export=True)
        fileops = {'defaultextension': '.csv',
                   'filetypes': [('text files', '.csv')],
                   'initialdir': self.options['etmdir'],
                   'title': 'CSV data files',
                   'parent': self}
        filename = asksaveasfilename(**fileops)
        if not filename:
            return False
        import csv as CSV
        c = CSV.writer(open(filename, "w"), delimiter=",")
        for line in data:
            c.writerow(line)

    def confirm(self, parent=None, title="", prompt="", instance="xyz"):
        ok, value = OptionsDialog(parent=parent, title=_("confirm").format(instance), prompt=prompt).getValue()
        return ok


class SimpleEditor(Toplevel):

    def __init__(self, parent=None, master=None, file=None, newhsh=None, rephsh=None, options=None, title=None, modified=False):
        """
        If file is given, open file for editing.
        Otherwise, we are creating a new item and/or replacing an item
        mode:
          1: new: edit newhsh, replace none
          2: replace: edit and replace rephsh
          3: new and replace: edit newhsh, replace rephsh

        :param parent:
        :param file: path to file to be edited
        """
        # self.frame = frame = Frame(parent)
        if master is None:
            master = parent
        self.master = master
        Toplevel.__init__(self, master)
        self.minsize(400, 300)
        self.geometry('500x200')
        self.transient(parent)
        self.configure(background=BGCOLOR, highlightbackground=BGCOLOR)
        self.parent = parent
        self.loop = parent.loop
        self.messages = self.loop.messages
        self.messages = []
        self.changed = False

        self.scrollbar = None
        self.listbox = None
        self.autocompletewindow = None
        self.line = None
        self.match = None

        self.file = file
        self.initfile = None
        self.fileinfo = None
        self.repinfo = None
        self.title = title
        self.newhsh = newhsh
        self.rephsh = rephsh
        self.value = ''
        self.options = options
        self.tkfixedfont = tkFont.nametofont("TkFixedFont")
        self.tkfixedfont.configure(size=self.options['fontsize_fixed'])
        # self.text_value.trace_variable("w", self.setSaveStatus)
        frame = Frame(self, bd=0, relief=FLAT)
        frame.pack(side="bottom", fill=X, padx=4, pady=0)
        frame.configure(background=BGCOLOR, highlightbackground=BGCOLOR)

        btnwdth = 5

        # ok will check, save and quit
        Button(frame, text=_("Save and Exit"), highlightbackground=BGCOLOR, command=self.onSave, pady=2).pack(side=RIGHT, padx=4)

        l, c = commandShortcut('w')
        self.bind(c, self.onSave)

        # quit with a warning prompt if modified
        Button(frame, text=_("Cancel"), highlightbackground=BGCOLOR, pady=2, command=self.quit).pack(side=LEFT, padx=4)
        # self.bind("<Escape>", self.quit)

        l, c = commandShortcut('q')
        self.bind(c, self.quit)
        self.bind("<Escape>", self.cancel)
        # check will evaluate the item entry and, if repeating, show reps
        inspect = Button(frame, text=_("Validate"), highlightbackground=BGCOLOR,  command=self.onCheck, pady=2)
        self.bind("<Control-question>", self.onCheck)
        inspect.pack(side=RIGHT, padx=4)

        # find
        Button(frame, text='x', command=self.clearFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)
        self.find_text = StringVar(frame)
        self.e = Entry(frame, textvariable=self.find_text, width=10, highlightbackground=BGCOLOR)
        self.e.pack(side=LEFT, padx=0, expand=1, fill=X)
        self.e.bind("<Return>", self.onFind)
        Button(frame, text='>', command=self.onFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)

        text = Text(self, wrap="word", bd=2, relief="sunken", padx=3, pady=2, font=self.tkfixedfont, undo=True, width=70)
        text.configure(highlightthickness=0)
        text.tag_configure(FOUND, background="lightskyblue")

        text.pack(side="bottom", padx=4, pady=3, expand=1, fill=BOTH)
        self.text = text

        self.completions = []
        completions = set([])
        if self.options['auto_completions']:
            cf = self.options['auto_completions']
            if os.path.isfile(cf):
                logger.debug("auto_completions: {0}".format(cf))
                fe = self.options['encoding']['file']
                with codecs.open(cf, 'r', fe) as fo:
                    for x in fo.readlines():
                        x = x.rstrip()
                        if x and x[0] != "#":
                            completions.add(x)
                logger.info('Using completions file: {0}'.format(cf))
            else:
                logger.warn("Could not find completions file: {0}".format(cf))
        else:
            logger.info("auto_completions not specified in etmtk.cfg")

        if self.options['shared_completions']:
            cf = self.options['shared_completions']
            if os.path.isfile(cf):
                logger.debug("shared_completions: {0}".format(cf))
                fe = self.options['encoding']['file']
                with codecs.open(cf, 'r', fe) as fo:
                    for x in fo.readlines():
                        x = x.rstrip()
                        if x and x[0] != "#":
                            completions.add(x)
                logger.info('Using shared completions file: {0}'.format(cf))
            else:
                logger.warn("Could not find shared completions file: {0}".format(cf))
        else:
            logger.info("optional shared_completions not specified in etmtk.cfg")

        if completions:
            self.completions = list(completions)
            self.completions.sort()


        if title is not None:
            self.wm_title(title)
        if file is not None:
            # we're editing a file
            self.mode = 'file'
            inspect.configure(state="disabled")
            if not os.path.isfile(file):
                logger.warn('could not open: {0}'.format(file))
                text = ""
            else:
                with codecs.open(file, 'r',
                             self.options['encoding']['file']) as f:
                    text = f.read()
        else:
            # we are creating a new item and/or replacing an item
            # mode:
            #   1: new
            #   2: replace
            #   3: new and replace
            self.initfile = initfile = ensureMonthly(options=self.options, date=datetime.now())
            # logger.debug("newhsh: {0}".format(self.newhsh))
            # logger.debug("rephsh: {0}".format(self.rephsh))
            # set the mode
            if newhsh is None and rephsh is None:
                # we are creating a new item from scratch
                self.mode = 1
                self.edithsh = self.newhsh
                text = ''
            elif rephsh is None:  # newhsh is not None
                # we are creating a new item as a copy
                self.mode = 1
                self.edithsh = self.newhsh
                if ('fileinfo' in newhsh and newhsh['fileinfo']):
                    initfile = newhsh['fileinfo'][0]
                text = hsh2str(self.edithsh, self.options)
            elif newhsh is None: # rephsh
                # we are editing and replacing rephsh - no file prompt
                self.mode = 2
                # self.repinfo = rephsh['fileinfo']
                self.edithsh = self.rephsh
                text = hsh2str(self.edithsh, self.options)
            else:  # neither is None
                # we are changing some instances of a repeating item
                # we will be writing but not editing rephsh using its fileinfo
                # we will be editing and saving newhsh using self.initfile
                self.mode = 3
                self.edithsh = self.newhsh
                # self.repinfo = rephsh['fileinfo']
                if 'fileinfo' in newhsh and newhsh['fileinfo'][0]:
                    initfile = self.newhsh['fileinfo'][0]
                text = hsh2str(self.edithsh, self.options)

            logger.debug('mode: {0}; initfile: {1}; edit: {2}'.format(self.mode,  self.initfile,  self.edithsh))
        # logger.debug("setting text {0}:\n{1}".format(type(text), text))
        self.settext(text)

        # clear the undo buffer
        if not modified:
            self.text.edit_reset()
            self.setmodified(False)
        self.text.bind('<<Modified>>', self.updateSaveStatus)

        self.text.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if parent:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))
        self.configure(background=BGCOLOR)
        l, c = commandShortcut('f')
        self.bind(c, lambda e: self.e.focus_set())
        l, c = commandShortcut('g')
        self.bind(c, lambda e: self.onFind())
        self.text.mark_set(INSERT, END)
        # l, c = commandShortcut('/')
        logger.debug("/: {0}, {1}".format(l, c))
        # self.text.bind("<Control-slash>", self.showCompletions)
        self.text.bind("<Control-space>", self.showCompletions)
        self.grab_set()

        self.wait_window(self)


    def settext(self, text=''):
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()
        logger.debug("modified: {0}".format(self.checkmodified()))

    def gettext(self):
        return self.text.get('1.0', END + '-1c')

    def setCompletions(self, *args):
        match = self.filterValue.get()
        self.matches = matches = [x for x in self.completions if x and x.lower().startswith(match.lower())]
        self.listbox.delete(0, END)
        for item in matches:
            self.listbox.insert(END, item)
        self.listbox.select_set(0)
        self.listbox.see(0)
        self.fltr.focus_set()

    def showCompletions(self, e=None):
        if not self.completions:
            return "break"
        if self.autocompletewindow:
            return "break"
        line = self.text.get("insert linestart", INSERT)
        m = completion_regex.search(line)
        if not m:
            logger.debug("no match in {0}".format(line))
            return "break"

        # set self.match here since it determines the characters to be replaced
        self.match = match = m.groups()[0]
        logger.debug("found match '{0}' in line '{1}'".format(match, line))

        self.autocompletewindow = acw = Toplevel(master=self.text)
        acw.geometry("+%d+%d" % (self.text.winfo_rootx() + 50,
                          self.text.winfo_rooty() + 50))

        self.autocompletewindow.wm_attributes("-topmost", 1)

        self.filterValue = StringVar(self)
        self.filterValue.set(match)
        self.filterValue.trace_variable("w", self.setCompletions)
        self.fltr = fltr = Entry(acw, textvariable=self.filterValue)
        self.fltr.pack(side="top", fill="x") #, expand=1, fill=X)
        self.fltr.icursor(END)

        self.listbox = listbox = Listbox(acw, exportselection=False, width=self.loop.options['completions_width'])
        listbox.pack(side="bottom", fill=BOTH, expand=True)

        self.autocompletewindow.bind("<Double-1>", self.completionSelected)
        self.autocompletewindow.bind("<Return>", self.completionSelected)
        self.autocompletewindow.bind("<Escape>", self.hideCompletions)
        self.autocompletewindow.bind("<Up>", self.cursorUp)
        self.autocompletewindow.bind("<Down>", self.cursorDown)
        self.fltr.bind("<Up>", self.cursorUp)
        self.fltr.bind("<Down>", self.cursorDown)
        self.setCompletions()


    def is_active(self):
        return self.autocompletewindow is not None

    def hideCompletions(self, e=None):
        if not self.is_active():
            return
        # destroy widgets
        # self.match = None
        # self.autocompletewindow.destroy()
        # self.scrollbar.destroy()
        # self.scrollbar = None
        self.listbox.destroy()
        self.listbox = None
        self.autocompletewindow.destroy()
        self.autocompletewindow = None

    def completionSelected(self, event):
        # Put the selected completion in the text, and close the list
        cursel = self.matches[int(self.listbox.curselection()[0])]
        start = "insert-{0}c".format(len(self.match))
        end = "insert-1c wordend"
        logger.debug("cursel: {0}; match: {1}; start: {2}; insert: {3}".format(
            cursel, self.match, start, INSERT))
        self.text.delete(start, end)
        self.text.insert(INSERT, cursel)
        self.hideCompletions()

    def cursorUp(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        # newsel = max(0, cursel=1)
        newsel = max(0, cursel-1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def cursorDown(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        newsel = min(len(self.matches)-1, cursel+1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def setmodified(self, bool):
        if bool is not None:
            self.text.edit_modified(bool)

    def checkmodified(self):
        return self.text.edit_modified()

    def updateSaveStatus(self, event=None):
        if self.checkmodified():
            self.wm_title("{0} *".format(self.title))
        else:
            self.wm_title(self.title)

    def onSave(self, e=None):
        e = None
        if not self.checkmodified():
            self.quit()
        elif self.file is not None:
            # we are editing a file
            alltext = self.gettext()
            self.loop.safe_save(self.file, alltext)
            # with codecs.open(self.file, 'w',
            #                  self.options['encoding']['file']) as f:
            #     f.write(alltext)
            self.setmodified(False)
            self.changed = True
            self.quit()
        else:
            # we are editing an item
            ok = self.onCheck(showreps=False, showres=False)
            if not ok:
                return "break"
            if self.mode in [1, 3]:  # new
                dir = self.options['datadir']
                if 's' in self.edithsh and self.edithsh['s']:
                    dt = self.edithsh['s']
                    file = ensureMonthly(self.options, dt.date())
                else:
                    dt = None
                    file = ensureMonthly(self.options)
                dir, initfile = os.path.split(file)
                # we need a filename for the new item
                # make datadir the root
                logger.debug('initial dir and file: "{0}"; "{1}"'.format(dir, initfile))
                fileops = {'defaultextension': '.txt',
                           'filetypes': [('text files', '.txt')],
                           'initialdir': dir,
                           'initialfile': initfile,
                           'title': 'etmtk data files',
                           'parent': self}
                filename = askopenfilename(**fileops)
                if not (filename and os.path.isfile(filename)):
                    return False
                else:
                    filename = os.path.normpath(filename)
                    logger.debug('saving to: {0}'.format(filename))
                    self.text.focus_set()
            logger.debug('edithsh: {0}'.format(self.edithsh))
            ok = True
            if self.mode == 1:
                if self.loop.append_item(self.edithsh, filename):
                    logger.debug('append mode: {0}'.format(self.mode))
                else:
                    ok = False
            elif self.mode == 2:
                if self.loop.replace_item(self.edithsh):
                    logger.debug('replace mode: {0}'.format(self.mode))
                else:
                    ok = False
            else:  # self.mode == 3
                if self.loop.append_item(self.edithsh, filename):
                    logger.debug('append mode: {0}'.format(self.mode))
                else:
                    ok = False
                if self.loop.replace_item(self.rephsh):
                    logger.debug('replace mode: {0}'.format(self.mode))
                else:
                    ok = False

            # update the return value so that when it is not null then modified
            # is false and when modified is true then it is null
            self.setmodified(False)
            self.changed = True
            self.quit()
            return "break"

    def onCheck(self, event=None, showreps=True, showres=True):
        self.loop.messages = []
        text = self.gettext()
        logger.debug("text: {0}".format(text))
        msg = []
        reps = []
        error = False
        hsh, msg = str2hsh(text, options=self.options)
        self.loop.messages.extend(msg)
        if self.loop.messages:
            messages = "{0}".format("\n".join(self.loop.messages))
            logger.debug("messages: {0}".format(messages))
            self.messageWindow(MESSAGES, messages, opts=self.options)
            return False

        # we have a good hsh
        if self.edithsh and 'fileinfo' in self.edithsh:
            fileinfo = self.edithsh['fileinfo']
            self.edithsh = hsh
            self.edithsh['fileinfo'] = fileinfo
        else:
            # we have a new item without fileinfo
            self.edithsh = hsh
        # update missing fields
        str = hsh2str(hsh, options=self.options)
        logger.debug("str: {0}".format(str))
        if str != text:
            self.settext(str)
        if 'r' in hsh and showreps:
            showing_all, reps =  get_reps(self.options['bef'], hsh)
            repsfmt = [x.strftime(rrulefmt) for x in reps]
            logger.debug("{0}: {1}".format(showing_all, repsfmt))

            repetitions = "{0}".format("\n".join(repsfmt))
            if showing_all:
                self.messageWindow(ALLREPS, repetitions, opts=self.options, width=24)
            else:
                self.messageWindow(SOMEREPS, repetitions, opts=self.options, width=24)
        elif showres:
            self.messageWindow(MESSAGES, _("valid entry"), opts=self.options, height=1, width=14)
        logger.debug(('onCheck: Ok'))
        return True

    def clearFind(self, *args):
        self.text.tag_remove(FOUND, "0.0", END)
        self.find_text.set("")

    def onFind(self, *args):
        target = self.find_text.get()
        logger.debug('target: {0}'.format(target))
        if target:
            where = self.text.search(target, INSERT, nocase=1)
        if where:
            pastit = where + ('+%dc' % len(target))
            # self.text.tag_remove(SEL, '1.0', END)
            self.text.tag_add(FOUND, where, pastit)
            self.text.mark_set(INSERT, pastit)
            self.text.see(INSERT)
            self.text.focus()

    def cancel(self, e=None):
        t = self.find_text.get()
        if t.strip():
            self.clearFind()
            return "break"
        if self.autocompletewindow:
            self.hideCompletions()
            return "break"
        # if self.checkmodified():
        #     return "break"
        logger.debug(('calling quit'))
        self.quit()

    def quit(self, e=None):
        if self.checkmodified():
            ans = self.confirm(parent=self,
                title=_('Quit'),
                prompt=_("There are unsaved changes.\nDo you really want to quit?"))
        else:
            ans = True
        if ans:
            if self.parent:
                logger.debug('focus set')
                self.master.focus()
                self.master.focus_set()
            self.destroy()
        return "break"

    def messageWindow(self, title, prompt, opts=None, height=14, width=52):
        win = Toplevel(self)
        win.title(title)
        win.geometry("+%d+%d" % (self.text.winfo_rootx() + 50,
                          self.text.winfo_rooty() + 50))
        # win.minsize(444, 430)
        # win.minsize(450, 450)
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active', pady=2)
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(
            f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            font=self.tkfixedfont,
            height=height,
            width=width,
            takefocus=False)
        t.insert("0.0", prompt)
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        # ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview)
        # ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
        # t.configure(state="disabled", yscroll=ysb.set)
        # t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)

        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def confirm(self, parent=None, title="", prompt="", instance="xyz"):
        ok, value = OptionsDialog(parent=parent, title=_("confirm").format(instance), prompt=prompt).getValue()
        return ok


if __name__ == '__main__':
    print('edit.py should only be imported. Run etm or view.py instead.')
