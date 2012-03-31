
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.morphology.service.ServicesLocator import *

from learnX.utils.Log import *

class JapaneseMorphemeModel(QAbstractTableModel):
    def __init__(self, deck, language, allDecks):
        QAbstractTableModel.__init__(self)
        
        self.servicesLocator = ServicesLocator.getInstance()
        
        self.morphemesService = self.servicesLocator.getMorphemesService()
        self.decksService = self.servicesLocator.getDecksService()
        
        self.decksId = decksId = []
        if allDecks:
            self.language = language
            self.decks = self.decksService.listDecksByLanguage(self.language)
            for deck in self.decks:
                decksId.append(deck.id)
        else:
            self.deck = deck
            decksId.append(deck.id)
        
        self.morphemes = self.morphemesService.getMorphemes(None, decksId)
        self.initMorphemesLen = len(self.morphemes)
        self.currentMorphemesLen = len(self.morphemes)
        
        self.columns = ["Expression", "Reading", "Part of Speech", "Sub P-o-S", "Status", "Changed", "Facts Count", "Score"]
        
    # Model interface
    ######################################################################

    def rowCount(self, index):
        return len(self.morphemes)

    def columnCount(self, index):
        return 8

    def headerData(self, section, orientation, role):
        if orientation == Qt.Vertical:
            return QVariant()
        elif role == Qt.DisplayRole:
            return QVariant(self.columns[section])
        elif role == Qt.FontRole:
            f = QFont()
            f.setPixelSize(12)
            return QVariant(f)
        else:
            return QVariant()

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            morpheme = self.morphemes[index.row()]
            morphemeLemme = morpheme.morphLemme
            
            s = ""
            columnId = index.column()
            if columnId == 0:
                s = morphemeLemme.base
            elif columnId == 1:
                s = morphemeLemme.read
            elif columnId == 2:
                s = morphemeLemme.pos
            elif columnId == 3:
                s = morphemeLemme.subPos
            elif columnId == 4:
                s = morpheme.getStatusName()
            elif columnId == 5:
                if morpheme.statusChanged:
                    s = "yes"
                else:
                    s = "no"
            elif columnId == 6:
                s = morpheme.factsCount  
            elif columnId == 7:
                s = int(morpheme.score)          
            return QVariant(s)
        else:
            return QVariant()
        
    def showMatching(self, force=True):
        
        self.morphemes = self.morphemesService.getMorphemes(self.searchText, self.decksId)
        self.currentMorphemesLen = len(self.morphemes)
        self.reset()