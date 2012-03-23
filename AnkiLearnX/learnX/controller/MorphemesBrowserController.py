from learnX.utils.Log import *
from learnX.interface.MorphemesBrowser import *

class MorphemesBrowserController:
    def __init__(self):
        test = "test"
    
    def launchBrowserMorphemes(self, deck):
        log("Launch Browser Morphemes")
        self.morphemesBrowser = MorphemesBrowser(deck)
        self.morphemesBrowser.show()