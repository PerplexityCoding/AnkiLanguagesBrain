#-*- coding: utf-8 -*-

#from ankiqt import mw, forms, ui
import datetime, os
import codecs

learnXPath = 'E:\Project\Git\AnkiLearnX\AnkiLearnX'
logPath = os.path.join(learnXPath, 'learnX', 'log', 'main.log')
#logPath = os.path.join(mw.pluginsFolder(), 'learnX', 'log', 'main.log')

VERBOSE = False
NO_LOG = False

################################################################################
## Log / inform system
################################################################################

def debug( msg ):
    if VERBOSE: log( msg )

def log( msg ):
    if NO_LOG: return
    txt = '%s: %s' % ( datetime.datetime.now(), msg )
    f = codecs.open( logPath, 'a', 'utf-8' )
    f.write( txt + '\n' )
    f.close()
    print txt

def clearLog():
   f = codecs.open( logPath, 'w', 'utf-8' )
   f.close()