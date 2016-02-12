#
# This file is a command-module for Dragonfly.
#

"""
Command-module for controlling basic media.
=====================================

This module implements basic media commands.

"""

import pkg_resources
pkg_resources.require("dragonfly >= 0.6.5beta1.dev-r76")
from dragonfly import (Grammar, Section, Item, MappingRule, Key, Integer)


class MediaControl(MappingRule):

    mapping  = {
                "(audio up | volume up | louder) [<n>]":             Key("volumeup:%(n)d/15"),
                "(audio down | volume down | softer) [<n>]":         Key("volumedown:%(n)d/15"),
                "(audio | sound) (mute | unmute | off | on)":        Key("volmute"), 
                "music (pause | play)":                              Key("playpause"), 
                "music next":                                        Key("tracknext"), 
                "music (last | previous)":                           Key("trackprev") 
                }
    extras   = [
                Integer("n", 1, 50)
                #Dictation("text"),
               ]
    defaults = {
                "n": 5,
               }


#---------------------------------------------------------------------------
# Create and manage this module's grammar.

grammar = Grammar("volume control")
grammar.add_rule(MediaControl())
grammar.load()
def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
