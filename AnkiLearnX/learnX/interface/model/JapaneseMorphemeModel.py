
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
        
        self.morphemes = self.morphemesService.getAllLemmes()
        self.initMorphemesLen = len(self.morphemes)
        self.currentMorphemesLen = len(self.morphemes)
        
        self.columns = ["Expression", "Reading", "Part of Speech", "Sub P-of-S", "Rank", "Interval", "Score"]
        
    # Model interface
    ######################################################################

    def rowCount(self, index):
        return len(self.morphemes)

    def columnCount(self, index):
        return len(self.columns)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Vertical:
            return None
        elif role == Qt.DisplayRole:
            return self.columns[section]
        elif role == Qt.FontRole:
            f = QFont()
            f.setPixelSize(12)
            return f
        else:
            return None

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            morpheme = self.morphemes[index.row()]
            
            s = ""
            columnId = index.column()
            if columnId == 0:
                s = morpheme.base
            elif columnId == 1:
                s = morpheme.read
            elif columnId == 2:
                s = morpheme.pos
            elif columnId == 3:
                s = morpheme.subPos
            elif columnId == 4:
                s = int(morpheme.rank)  
            elif columnId == 5:
                s = int(morpheme.maxInterval)   
            elif columnId == 6:
                s = int(morpheme.score)            
            return s
        else:
            return None
        
    def showMatching(self, force=True):
        
        self.morphemes = self.morphemesService.getMorphemes(self.searchText, self.decksId)
        self.currentMorphemesLen = len(self.morphemes)
        self.reset()