from anki.hooks import addHook
from ankiqt import mw

def setup():
    import learnX.interface.main

mw.registerPlugin( 'LearnX', 17201108172229 )
addHook('init', setup)
