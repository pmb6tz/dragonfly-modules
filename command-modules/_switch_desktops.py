#
# This file is a command-module for Dragonfly.
#

"""
Command-module for switching virtual desktops in Windows 10.
=====================================

This module implements commands to manipulate virtual desktops. 
Navigate between them, create, and delete. 

NOTE: In order to navigate by number, you'll need this AutoHotKey script:
https://github.com/pmb6tz/windows-desktop-switcher

"""

import pkg_resources
pkg_resources.require("dragonfly >= 0.6.5beta1.dev-r76")
from dragonfly import (Grammar, Section, Item, MappingRule, Key, Integer)


class DesktopSwitcher(MappingRule):

    mapping  = {
                "(screen | desktop) [<n>]":     Key("ca-%(n)d/15"),     # see note above to use this
                "(screen | desktop) right":     Key("cw-right"),
                "(screen | desktop) left":      Key("cw-left"),
                "create desktop":               Key("ca-c/15"),         # see note above to use this
                "delete desktop":               Key("ca-d/15")          # see note above to use this
                }
    extras   = [
                Integer("n", 1, 9)
                #Dictation("text"),
               ]
    defaults = {
                "n": 1,
               }


#---------------------------------------------------------------------------
# Create and manage this module's grammar.

grammar = Grammar("switch desktops")
grammar.add_rule(DesktopSwitcher())
grammar.load()
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
