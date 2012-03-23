#-*- coding: utf-8 -*-

from ankiqt import mw

from learnX.utils.Log import *
from learnX.morphology.service import *
from learnX.morphology.service.DecksService import *
from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.MorphemesService import *

from learnX.interface.LanguageChooser import *
from learnX.interface.DeckConfig import *

from learnX.controller.LearnXMainController import *
from learnX.controller.MorphemesBrowserController import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from anki.deck import DeckStorage

import datetime, os

class LearnX(QDialog):
    def __init__(self, parent=None):
        super(LearnX, self).__init__(parent)
        self.mw = parent
        self.setWindowTitle('LearnX')
        self.resize(600, 0)
        
        self.decksService = DecksService()
        self.languagesService = LanguagesService()
        self.morphemesService = MorphemesService()
        
        self.mainController = LearnXMainController()
        self.morphemesController = MorphemesBrowserController()
        
        self.mainVBox = mainVBox = QVBoxLayout(self)
        
        self.setupMain()
        self.setupDecks()
        self.setupLanguages()
        self.setupToolbar()
        
    def refreshAll(self):
        
        mainVBox = self.mainVBox
        
        mainVBox.removeWidget(self.decksTitle)
        self.decksTitle.deleteLater()
        
        mainVBox.removeWidget(self.languagesTitle)
        self.languagesTitle.deleteLater()
        
        mainVBox.removeWidget(self.toolBarFrame)
        self.toolBarFrame.deleteLater()
        
        self.setupMain()
        self.setupDecks()
        self.setupLanguages()
        self.setupToolbar()
        
    def tableTitle(self, title):
        
        titleFont = QFont("Arial", 9, QFont.Bold)
        qlabel = QLabel(title)
        qlabel.setFont(titleFont)
        
        return qlabel
        
    def setupMain(self):
        
        mainVBox = self.mainVBox
        
        mainVBox.setSpacing(0)
        mainVBox.setSizeConstraint(QLayout.SetMinAndMaxSize)
        
        self.titleFont = titleFont = QFont("Arial", 14)
        
        self.decksTitle = decksTitle = QGroupBox("Decks")
        mainVBox.decksGrid = decksGrid = QGridLayout()
        
        self.decksTitle.setLayout(decksGrid)
        mainVBox.addWidget(decksTitle)
        
        decksGrid.addWidget(self.tableTitle("Deck"), 0, 0)
        decksGrid.addWidget(self.tableTitle("Total"), 0, 1, Qt.AlignHCenter)
        decksGrid.addWidget(self.tableTitle("Known"), 0, 2, Qt.AlignHCenter)
        decksGrid.addWidget(self.tableTitle("Mature"), 0, 3, Qt.AlignHCenter)
        decksGrid.addWidget(self.tableTitle("Actions"), 0, 4, 1, 3, Qt.AlignHCenter)
        
        self.languagesTitle = languagesTitle = QGroupBox('Languages')
        
        mainVBox.languagesGrid = languagesGrid = QGridLayout()
        languagesTitle.setLayout(languagesGrid)
        
        mainVBox.addWidget(languagesTitle)

    def enabledDeck(self, deck, index):
        
        checkBox = self.checkBoxes[index]
        
        log(checkBox.isChecked())
        if checkBox.isChecked():
            deck = self.decksService.enableDeck(deck)
        else:
            deck = self.decksService.disableDeck(deck)
        
        conf = self.confButtons[index]
        conf.setEnabled(deck.enabled)
        log(deck.enabled)
    
    def configDeck(self, deck):

        self.deckConfig = DeckConfig(deck, self)
        self.deckConfig.show()

    def setupDecks(self):
        
        decksGrid = self.mainVBox.decksGrid
        
        i = 1
        self.confButtons = []
        self.checkBoxes = []
        for deckSummary in self.mw.browserDecks:
            
            deck = self.decksService.getDeck(deckSummary["name"], deckSummary["path"])
            
            checkBox = QCheckBox(deck.name)
            checkBox.setChecked(deck.enabled)
            self.checkBoxes.append(checkBox)
            
            self.connect(checkBox, SIGNAL("clicked()"), lambda j=i-1, d=deck: self.enabledDeck(d,j))
            
            decksGrid.addWidget(checkBox, i, 0)
            
            if deck.enabled:
                decksGrid.addWidget(QLabel(str(deck.totalMorphemes)), i, 1, Qt.AlignHCenter)
                decksGrid.addWidget(QLabel(str(deck.knownMorphemes)), i, 2, Qt.AlignHCenter)
                decksGrid.addWidget(QLabel(str(deck.matureMorphemes)), i, 3, Qt.AlignHCenter)
            
            conf = QPushButton("Conf")
            self.confButtons.append(conf)
            conf.setEnabled(deck.enabled)
            
            self.connect(conf, SIGNAL("clicked()"), lambda d=deck: self.configDeck(d))
            
            decksGrid.addWidget(conf, i, 4)
        
            # on peux browse meme si desactivé, si le total de morphemes n'ai pas nulle
            analyze = QPushButton("Analyze")
            analyze.setEnabled(deck.enabled and deck.language != None)
            self.connect(analyze, SIGNAL("clicked()"), lambda d=deck: self.mainController.launchAnalyze(d))
            decksGrid.addWidget(analyze, i, 5)
            
            more = QPushButton("More")
            more.setEnabled(deck.enabled and deck.language != None and deck.totalMorphemes > 0)
            self.connect(more, SIGNAL("clicked()"), lambda d=deck: self.morphemesController.launchBrowserMorphemes(d))
            decksGrid.addWidget(more, i, 6)
            i += 1
        
        decksGrid.setRowStretch(1, 1)
        decksGrid.setRowStretch(1, 0)
    
    def refreshLanguages(self):
        
        #languagesFrame = self.mainVBox.languagesFrame

        #self.mainVBox.languagesGrid = languagesGrid = QGridLayout()
        
        languagesGrid = self.mainVBox.languagesGrid
        
        languagesGrid.children()
        
        self.setupLanguages()
        
        languagesFrame.setLayout(languagesGrid)
        languagesFrame.invalidate()
        
        self.mainVBox.update()
        
    def setupLanguages(self):
        languagesGrid = self.mainVBox.languagesGrid
        
        i = 1
        
        languages = self.languagesService.listLanguages()
        
        if len(languages) > 0:
            languagesGrid.addWidget(self.tableTitle("Language"), 0, 0)
            languagesGrid.addWidget(self.tableTitle("Total"), 0, 1, Qt.AlignHCenter)
            languagesGrid.addWidget(self.tableTitle("Known"), 0, 2, Qt.AlignHCenter)
            languagesGrid.addWidget(self.tableTitle("Mature"), 0, 3, Qt.AlignHCenter)
            languagesGrid.addWidget(self.tableTitle("Actions"), 0, 4, 1, 3, Qt.AlignHCenter)
        
        for language in languages:
            languageName = self.languagesService.getLanguageNameFromCode(language.nameId)
            log(languageName)
            languagesGrid.addWidget(QLabel(languageName), i, 0)
            
            conf = QPushButton("Conf")
            self.confButtons.append(conf)
            languagesGrid.addWidget(conf, i, 4)
        
            # on peux browse meme si desactivé, si le total de morphemes n'ai pas nulle
            run = QPushButton("Run")
            #run.setEnabled(deck.totalMorphemes > 0)
            languagesGrid.addWidget(run, i, 5)
            
            more = QPushButton("More")
            languagesGrid.addWidget(more, i, 6)
            
            i += 1
        
        addNewLanguageButton = QPushButton("Add New Language")
        mw.connect(addNewLanguageButton, SIGNAL('clicked()'), self.openLanguageChooser)
        languagesGrid.addWidget(addNewLanguageButton, i, 0, 1, 4)

    def openLanguageChooser(self):
        self.languageChooser = LanguageChooser(self)
        self.languageChooser.show()
        
    def setupToolbar(self):
        mainVBox = self.mainVBox
        
        self.toolBarFrame = toolBarFrame = QGroupBox("Actions")

        mainVBox.toolBarLayout = toolBarLayout = QHBoxLayout()
        toolBarFrame.setLayout(toolBarLayout)
        
        toolBarLayout.addWidget(QPushButton("Run All"))
        
        
        mainVBox.addWidget(toolBarFrame)
    
def openWindows():
    mw.mainWin.learnX = LearnX(mw)
    mw.mainWin.learnX.show()

def init():
    mw.mainWin.learnXAction = QAction('LearnX', mw)
    mw.connect(mw.mainWin.learnXAction, SIGNAL('triggered()'), openWindows)
    mw.mainWin.toolBar.addAction(mw.mainWin.learnXAction)

log("OK")
mw.addHook('init', init)