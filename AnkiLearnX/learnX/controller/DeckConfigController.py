
#from anki.models import FieldModel
import anki.stdmodels

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class DeckConfigController:
    def __init__(self, interface):
        self.interface = interface
        self.parent = interface.parent
        self.deck = interface.deck
        
        self.deckManager = interface.deckManager
        
        self.decksService = self.parent.decksService
        
    def saveConfig(self):
        
        interface = self.interface
        
        if interface.languageCombo.currentIndex() <= 0:
            # Error : marked in red + Error message
            return
        if interface.expressionCombo.currentIndex() <= 0:
            # Error : marked in red + Error message
            return

        mainVBox = interface.mainVBox
        deck = interface.deck
        realDeck = self.deckManager.get(deck.id)

        self.decksService.changeLanguage(interface.deck, unicode(interface.languageCombo.currentText()))
        
        deck.expressionField = str(interface.expressionCombo.currentText())
        
        bsPosListWidget = interface.bsPosListWidget
        disabledPosList = list()
        items = bsPosListWidget.findItems("*", Qt.MatchWrap | Qt.MatchWildcard)
        for item in items:
            log(item)
            disabledPosList.append(unicode(item.text()))
        deck.posOptions["disabledPos"] = disabledPosList

        self.decksService.updateDeck(deck)
        
        interface.parent.refreshAll()
        interface.close()
        