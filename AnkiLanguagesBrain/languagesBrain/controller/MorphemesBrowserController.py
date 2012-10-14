from languagesBrain.utils.Log import *
from languagesBrain.interface.MorphemesBrowser import *

class MorphemesBrowserController:
    def __init__(self):
        test = "test"
    
    def launchBrowserMorphemes(self, deck):
        log("Launch Browser Morphemes")
        self.morphemesBrowser = MorphemesBrowser(deck, deck.language, False)
        self.morphemesBrowser.show()
        
    def launchBrowserMorphemesByLanguage(self, language):
        log("Launch Browser Morphemes By Language")
        self.morphemesBrowser = MorphemesBrowser(None, language, True)
        self.morphemesBrowser.show()
        