
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from languagesBrain.morphology.service.ServicesLocator import *

from languagesBrain.utils.Log import *

class FrenchMorphemeModel(QAbstractTableModel):
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
        
        self.columns = ["Expression", "Part of Speech", "Status", "Changed", "Notes Count", "Score"]
        
    # Model interface
    ######################################################################

    def rowCount(self, index):
        return len(self.morphemes)

    def columnCount(self, index):
        return 6

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
                s = morphemeLemme.pos
            elif columnId == 2:
                s = morpheme.getStatusName()
            elif columnId == 3:
                if morpheme.statusChanged:
                    s = "yes"
                else:
                    s = "no"
            elif columnId == 4:
                s = morpheme.notesCount  
            elif columnId == 5:
                s = int(morpheme.score)          
            return QVariant(s)
        else:
            return QVariant()
        
    def showMatching(self, force=True):
        
        self.morphemes = self.morphemesService.getMorphemes(self.searchText, self.decksId)
        self.currentMorphemesLen = len(self.morphemes)
        self.reset()