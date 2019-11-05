#!/usr/bin/env python2
# encoding: utf-8

# This file is part of steam-shortcuts-gen.
#
# Copyright (c) 2018 Corporal Quesadilla
# Modifications (c) 2019 Andrew Steel <copyright@andrewsteel.net>
#
# SPDX-License-Identifier: GPL-3.0-only
#
# The GNU General Public License Version 3 only:
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 3
# as published by the Free Software Foundation.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file. If not, see <https://www.gnu.org/licenses/>.

# Usage:
#
# Argument                 Explanation
# --------                 -----------
# Path to Shortcuts.vdf    Requires Your personal ID - steamID3 [U:1:THIS_PART_HERE_COPY_ME] from https://steamidfinder.com/
#                              This is for the local path to your shortcuts.vdf file we're modifying,
#                              located in \Path\To\Steam\userdata\USERIDHERE\config\shortcuts.vdf. Use double quotes.
# Name of program          Whatever you want to call it. In double quotes if it has spaces or other funky characters
# Path to program or URL   In double quotes if the path has spaces or other funky characters
# Path to start program    Basically the folder it's in (use double quotes)
# Path to icon             Optional place to source the icon. In double quotes. BTW, I'm not sure where the Grid/BigPicture image comes from
# Shortcut path            No idea what this is. Just do "" (literally 'the empty string' - two double quotes in a row)
# Launch options           Probably needs double quotes if you got any spaces or other funky characters in there
# Hidden?                  Put a 1 here to make it only visible under "Hidden", anything else won't hide it. You need something though. 0 is fine.
# Allow Desktop Config?    Use controller's Desktop Configurations in this game. Put a 1 to enable it, anything else to disable. You need something though. 0 is fine.
# Allow Steam Overlay?     Put a 1 to enable it, anything else to disable. You need something though. 0 is fine.
# In VR library?           For the 'VR Library' Category. Put a 1 to enable it, anything else to disable. You need something though. 0 is fine.
# Last Play Time           Date last played. No idea how this works yet. For now, put 0 and I'll take care of it (mark it as "Never Played")
# Categories               Any categories you want it to appear in. If you use spaces in a category name, put it in double quotes
#
# Example:
# python2 steam-shortcuts.py "${HOME}/.local/share/Steam/userdata/ID_HERE/config/shortcuts.vdf" WoohooMyProgramWorks /usr/bin/game /usr/bin /usr/share/icons/hicolor/64x64/apps/game.png "" "-config default.cfg" 0 1 1 0 0 "tag (1)" "tag (2)"

import sys
from steam import filename_for_shortcut

def findLastEntryNumberAndPosition (pathToShortcutsVDF):
    # From the end, search backwards to the beginning of the last entry to get it's ID
    foundChars = 1
    target = '\x00\x01appname'
    lookingfor = 'target'
    lastEntryNumber = 0
    lastEntryPosition = 0

    f = open(str(pathToShortcutsVDF), 'r')
    fileContents = f.read()

    for i in range(len(fileContents)):
        if lookingfor == 'target':
            if (fileContents[-i]) == target[-foundChars]:
                #print repr(target[-foundChars]) + " found"
                foundChars = foundChars + 1
                if foundChars > len(target):
                    lookingfor = 'number'
            else:
                foundChars = 1
                # make sure current character didn't 'restart' the pattern
                # yeah I know copy-paste code sucks
                if (fileContents[-i]) == target[-foundChars]:
                    #print repr(target[-foundChars]) + " found"
                    foundChars = foundChars + 1
                    if foundChars > len(target):
                        lookingfor = 'number'
        else:
            if (fileContents[-i]).isdigit():
                #print repr(fileContents[-i]) + " found"
                lastEntryNumber = str((fileContents[-i])) + str(lastEntryNumber)
                lastEntryPosition = len(fileContents) - i
            else:
                break
    f.close()
    # Although unneccessary, also return the character position of the last entry's ID
    return (lastEntryNumber, lastEntryPosition)

def addEntry (pathToShortcutsVDF, inputTuple):
    # Entries are added before the last two characters of the file
    f = open(str(pathToShortcutsVDF), 'r+')
    fileContents = f.read()
    f.seek(len(fileContents) - 2)
    endFileContents = f.read()
    f.seek(len(fileContents) - 2)
    f.write(createEntry(inputTuple) + endFileContents)
    f.close()

def createEntry (inputTuple):
    # Put together all the variables and delimiters

    var_entryID         = inputTuple[0]
    var_appName         = inputTuple[1]
    var_unquotedPath    = inputTuple[2]
    var_startDir        = inputTuple[3]
    var_iconPath        = inputTuple[4]
    var_shortcutPath    = inputTuple[5]
    var_launchOptions   = inputTuple[6]
    var_isHidden        = inputTuple[7]
    var_allowDeskConf   = inputTuple[8]
    var_allowOverlay    = inputTuple[9]
    var_openVR          = inputTuple[10]
    var_lastPlayTime    = inputTuple[11]
    var_tags            = inputTuple[12]


    # There are several parts to an entry, all on one line
    # The data type refers to the input - \x01 indicates String, \x02 indicates boolean, \x00 indicates list
    # Strings must be encapsulated in quotes (aside from launch options)
    # Bools treat '\x01' as True and '\x00' as False
    # Lists are as follows: '\x01' + index + '\x00' + tagContents + '\x00'
    # I have no idea about Date. Not sure why LastPlayTime is marked as a bool
    #   4 characters, usually ending in '[' (maybe?). All 4 being '\x00' is fine too (default?).


    # Key                # Data Type  # Internal Name       # Delimiter     # Input             # Delimiter
    full_entryID        =                                      '\x00'  +  var_entryID        +  '\x00'
    full_appName        =  '\x01'  +  'appname'             +  '\x00'  +  var_appName        +  '\x00'
    full_quotedPath     =  '\x01'  +  'exe'                 +  '\x00'  +  var_unquotedPath   +  '\x00'
    full_startDir       =  '\x01'  +  'StartDir'            +  '\x00'  +  var_startDir       +  '\x00'
    full_iconPath       =  '\x01'  +  'icon'                +  '\x00'  +  var_iconPath       +  '\x00'
    full_shortcutPath   =  '\x01'  +  'ShortcutPath'        +  '\x00'  +  var_shortcutPath   +  '\x00'
    full_launchOptions  =  '\x01'  +  'LaunchOptions'       +  '\x00'  +  var_launchOptions  +  '\x00'
    full_isHidden       =  '\x02'  +  'IsHidden'            +  '\x00'  +  var_isHidden       +  '\x00\x00\x00'
    full_allowDeskConf  =  '\x02'  +  'AllowDesktopConfig'  +  '\x00'  +  var_allowDeskConf  +  '\x00\x00\x00'
    full_allowOverlay   =  '\x02'  +  'AllowOverlay'        +  '\x00'  +  var_allowOverlay   +  '\x00\x00\x00'
    full_openVR         =  '\x02'  +  'OpenVR'              +  '\x00'  +  var_openVR         +  '\x00\x00\x00'
    full_lastPlayTime   =  '\x02'  +  'LastPlayTime'        +  '\x00'  +  var_lastPlayTime
    full_tags           =  '\x00'  +  'tags'                +  '\x00'  +  var_tags           +  '\x08\x08'

    newEntry = full_entryID + full_appName + full_quotedPath + full_startDir + full_iconPath + full_shortcutPath + full_launchOptions + full_isHidden + full_allowDeskConf + full_allowOverlay + full_openVR + full_tags
    return newEntry
    pass

def inputPreperation (args, lastEntryInfo):
    # Get all the variables cleaned up

    # This is the newest entry, one more than the last one.
    var_entryID = str(int(lastEntryInfo[0])+1)

    # Strings
    var_appName         = args[2]
    var_unquotedPath    = args[3]
    var_startDir        = args[4]
    var_iconPath        = args[5]
    var_shortcutPath    = args[6] # what is this?
    var_launchOptions   = args[7]

    # Boolean checks
    if args[8] == '1':
        var_isHidden = '\x01'
    else:
        var_isHidden = '\x00'
    if args[9] == '1':
        var_allowDeskConf = '\x01'
    else:
        var_allowDeskConf = '\x00'
    if args[10] == '1':
        var_allowOverlay = '\x01'
    else:
        var_allowOverlay = '\x00'
    if args[11] == '1':
        var_openVR = '\x01'
    else:
        var_openVR = '\x00'

    # Date
    # Since the format hasn't been cracked yet, I'll populate with default
    #   values if you just pass in a '0'. Thank me later.
    var_tags= ''
    if args[12] == '0':
        var_lastPlayTime = '\x00\x00\x00\x00'
    else:
        var_lastPlayTime = args[12]

    for tag in range(13,len(args)-1):
        var_tags = var_tags + '\x01' + str(tag-13) + '\x00' + args[tag] + '\x00'

    return (var_entryID, var_appName, var_unquotedPath, var_startDir, var_iconPath, var_shortcutPath, var_launchOptions, var_isHidden, var_allowDeskConf, var_allowOverlay, var_openVR, var_lastPlayTime, var_tags)

def getURL (inputTuple):
    return filename_for_shortcut(inputTuple[2], inputTuple[1])

def main ():
    pathToShortcutsVDF = sys.argv[1]
    # fileExistenceCheck() # check if file exists. NOT IMPLEMENTED YET.
    lastEntryInfo = findLastEntryNumberAndPosition(pathToShortcutsVDF)
    inputTuple = inputPreperation(sys.argv, lastEntryInfo)
    addEntry(pathToShortcutsVDF, inputTuple)

    print getURL(inputTuple)

main()
