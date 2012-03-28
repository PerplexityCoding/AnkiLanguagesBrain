
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.morphology.service.ServicesLocator import *

from learnX.utils.Log import *

class MecabMorphemeModel(QAbstractTableModel):
    def __init__(self, deck, language=None):
        QAbstractTableModel.__init__(self)
        
        self.servicesLocator = ServicesLocator.getInstance()
        
        self.morphemesService = self.servicesLocator.getMorphemesService()
        self.decksService = self.servicesLocator.getDecksService()
        
        self.decksId = decksId = []
        if language != None:
            self.language = language
            self.decks = self.decksService.listDecksByLanguage(language)
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
        #if not index.isValid():
        #    return QVariant()
        #if role == Qt.FontRole:
        #    f = QFont()
        #    f.setPixelSize(self.parent.config['editFontSize'])
        #    return QVariant(f)
        #if role == Qt.TextAlignmentRole and index.column() == 2:
        #    return QVariant(Qt.AlignHCenter)
        #else:
        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            morpheme = self.morphemes[index.row()]
            s = ""
            columnId = index.column()
            if columnId == 0:
                s = morpheme.morph.base
            elif columnId == 1:
                s = morpheme.morph.read
            elif columnId == 2:
                s = morpheme.morph.pos
            elif columnId == 3:
                s = morpheme.morph.subPos
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
        #elif role == Qt.UserRole:
            
        else:
            return QVariant()
        
    def showMatching(self, force=True):
        
        self.morphemes = self.morphemesService.getMorphemes(self.searchText, self.decksId)
        self.currentMorphemesLen = len(self.morphemes)
        self.reset()