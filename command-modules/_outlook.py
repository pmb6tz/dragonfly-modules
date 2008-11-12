﻿#
# This file is a command-module for Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

"""
Command-module for **Microsoft Outlook** control
================================================

This module offers a number of commands for direct and efficient
control of Microsoft outlook.

Commands
--------

Command: **"(folder | show me) <folder>"**
    Jump straight to the specified folder.

Command: **"move to <folder>"**
    Move the selected item(s) to the specified folder.

Command: **"[create] new <type>"**
    Creates a new item of the specified type.

Command: **"(folder | show me) <folder>"**
    Jump straight to the specified folder.

Command: **"(synchronize | update) (folders | folder list)"**
    Update this module's internal list of Outlook folders.

"""


#---------------------------------------------------------------------------

from win32com.client                import constants
from pywintypes                     import com_error

from dragonfly.grammar.grammar      import ConnectionGrammar
from dragonfly.grammar.context      import AppContext
from dragonfly.grammar.elements     import DictListRef, Choice
from dragonfly.grammar.compoundrule import CompoundRule
from dragonfly.grammar.list         import DictList
from dragonfly.config               import Config, Section, Item


#---------------------------------------------------------------------------
# Set up this module's configuration.

config = Config("Microsoft Outlook control")
config.lang                 = Section("Language section")
config.lang.go_to_folder    = Item("(folder | show me) <folder>")
config.lang.move_to_folder  = Item("move to <folder>")
config.lang.create_new_item = Item("[create] new <type>")
config.lang.sync_folders    = Item("(synchronize | update) (folders | folder list)")
config.lang.item_type_mail  = Item("(mail | email)")
config.lang.item_type_task  = Item("task")
#config.generate_config_file()
config.load()


#---------------------------------------------------------------------------
# Utility generator function for iterating over COM collections.

def collection_iter(collection):
    for index in xrange(1, collection.Count + 1):
        yield collection.Item(index)

#---------------------------------------------------------------------------
# This module's main grammar.

class ControlGrammar(ConnectionGrammar):

    def __init__(self):
        self.folders = DictList("folders")
        ConnectionGrammar.__init__(
            self,
            name=self.__class__.__name__,
            context=AppContext(executable="outlook"),
            app_name="Outlook.Application"
           )

    def connection_up(self):
        # Made connection with Outlook -> retrieves available folders.
        self.update_folders()

    def connection_down(self):
        # Lost connection with Outlook -> empty folders list.
        self.reset_folders()

    def update_folders(self):
        namespace = self.application.GetNamespace("MAPI")
        inbox_folder = namespace.GetDefaultFolder(constants.olFolderInbox)
        root_folder = inbox_folder.Parent
        self.folders.set({})
        stack = [collection_iter(root_folder.Folders)]
        while stack:
            try:
                folder = stack[-1].next()
            except StopIteration:
                stack.pop()
                continue
            self.folders[folder.Name] = folder
            stack.append(collection_iter(folder.Folders))

    def reset_folders(self):
        self.folders.set({})

    def get_active_explorer(self):
        try:
            explorer = self.application.ActiveExplorer()
        except com_error, e:
            self._log.warning("%s: COM error getting active explorer: %s"
                              % (self, e))
            return None

        if not explorer:
            self._log.warning("%s: no active explorer." % self)
            return None
        return explorer

grammar = ControlGrammar()


#---------------------------------------------------------------------------
# Synchronize folders rule for explicitly updating folder list.

class SynchronizeFoldersRule(CompoundRule):
    spec = config.lang.sync_folders
    def _process_recognition(self, node, extras):
        self.grammar.update_folders()

grammar.add_rule(SynchronizeFoldersRule())


#---------------------------------------------------------------------------

class GoToFolderRule(CompoundRule):

    spec = config.lang.go_to_folder
    extras = [DictListRef("folder", grammar.folders)]

    def _process_recognition(self, node, extras):
        folder = extras["folder"]

        # Get the currently active explorer.
        explorer = self.grammar.get_active_explorer()
        if not explorer: return

        # Make the explorer view the given folder.
        explorer.SelectFolder(folder)

grammar.add_rule(GoToFolderRule())


#---------------------------------------------------------------------------

class MoveToFolderRule(CompoundRule):

    spec = config.lang.move_to_folder
    extras = [DictListRef("folder", grammar.folders)]

    def _process_recognition(self, node, extras):
        folder = extras["folder"]

        # Get the currently active explorer.
        explorer = self.grammar.get_active_explorer()
        if not explorer: return

        # Move the selected items to the given folder.
        for item in collection_iter(explorer.Selection):
            self._log.debug("%s: moving item %r to folder %r."
                            % (self, item.Subject, folder.Name))
            print ("%s: moving item %r to folder %r."
                   % (self, item.Subject, folder.Name))
            item.Move(folder)

grammar.add_rule(MoveToFolderRule())


#---------------------------------------------------------------------------
# Simple new item rule.

class NewItemRule(CompoundRule):

    spec = config.lang.create_new_item
    types = {        # Use delayed constant lookups, because these
                     #  are loaded when the com connection is set up.
             config.lang.item_type_mail:    "olMailItem",
             config.lang.item_type_task:    "olTaskItem",
            }
    extras = [Choice("type", types)]

    def _process_recognition(self, node, extras):
        item_type = getattr(constants, extras["type"])
        item = self.grammar.application.CreateItem(item_type)
        item.Display()

grammar.add_rule(NewItemRule())


#---------------------------------------------------------------------------
# Load the grammar instance and define how to unload it.

grammar.load()

# Unload function which will be called by natlink at unload time.
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None