#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.utils.Log import *
from learnX.controller.DeckConfigController import *
from learnX.morphology.service.ServicesLocator import *

from aqt import mw
#from anki.models import FieldModel
import anki.stdmodels

class DeckConfig(QDialog):
    def __init__(self, deck, parent=None):
        super(DeckConfig, self).__init__(parent)
        
        self.parent = parent
        self.deck = deck
        self.setWindowTitle('Configure Deck Option')
        self.resize(600, 0)
        
        self.deckManager = parent.deckManager
        self.modelManager = parent.modelManager

        self.mainVBox = mainVBox = QVBoxLayout(self)
        self.controller = DeckConfigController(self)
        
        self.languagesService = ServicesLocator.getInstance().getLanguagesService()
        
        self.setupLanguages()        
        self.setupExpression()
        #self.setupFields()
        #self.setupModes()
        self.setupPOSOptions()
        self.setupOptions()
        self.setupButtons()
        
    def setupLanguages(self):
        mainVBox = self.mainVBox
        deck = self.deck
        mainVBox.chooseHbox = chooseHbox = QHBoxLayout()
        
        chooseHbox.addWidget(QLabel("   (1) Choose Language"))
        
        self.languageCombo = languageCombo = QComboBox()
        
        languagesNameAvailable = self.languagesService.getAvailableLanguageName()
        #log(languagesName)

        currentIndex = 0
        languageCombo.addItem("------------------------")
        for languageName in languagesNameAvailable:
            languageCode = self.languagesService.getCodeFromLanguageName(languageName)
            log(languageCode)
            log(deck.language)
            if deck.language != None and deck.language.nameId == languageCode:
                currentIndex = languageCombo.count()
            languageCombo.addItem(languageName)
        
        languageCombo.setCurrentIndex(currentIndex)
        mw.connect(languageCombo, SIGNAL("activated(int)"), self.chooseLanguage)
        
        chooseHbox.addWidget(languageCombo)
        mainVBox.addLayout(chooseHbox)
        
    def setupExpression(self):
        mainVBox = self.mainVBox
        deck = self.deck
        ankiDeck = self.deckManager.get(deck.ankiDeckId)
        
        expressionFrame = QGroupBox("(2) Choose Expression")
        
        layout = QHBoxLayout()
        
        labelExpression = QLabel("Expression Field: ")

        self.expressionCombo = expressionCombo = QComboBox()
        expressionCombo.addItem("------------------------")
                
        allFields = list()
        for model in self.modelManager.all():
            for fieldName in self.modelManager.fieldNames(model):
                if fieldName not in allFields:
                    allFields.append(fieldName)
        allFields.sort()
        selectIndex = 0
        i = 1
        for fieldName in allFields:
            expressionCombo.addItem(fieldName)
            if fieldName == deck.expressionField:
                selectIndex = i
            i += 1
        expressionCombo.setCurrentIndex(selectIndex)
        
        layout.addWidget(labelExpression)
        layout.addWidget(expressionCombo)
        
        expressionFrame.setLayout(layout)
        
        mainVBox.addWidget(expressionFrame)
        
    def setupFields(self):
        
        mainVBox = self.mainVBox
        
        fieldsFrame = QGroupBox("(3) Choose Fields Option")
        
        mainVBox.fieldsGrid = fieldsGrid = QGridLayout()
        fieldsFrame.setLayout(fieldsGrid)
        
        fieldsGrid.setHorizontalSpacing(25)
        
        self.fieldsComponents = []
        fields = self.deck.fields
        if fields:
            i = 0
            j = 0
            
            for fieldKey in self.deck.fieldsList:
                fieldsGrid.addLayout(self.createField(fieldKey, fields[fieldKey][0], fields[fieldKey][1]), j, i)
                i += 1
                if i == 3:
                    i = 0
                    j += 1
        
        mainVBox.addWidget(fieldsFrame)
        
    def enableDefinitionModes(self):
        self.definitionKeyCombo.setEnabled(self.defintionCB.isChecked())
        self.definitionKeyCombo.setEnabled(self.defintionCB.isChecked())
        
    def setupModes(self): 
        
        mainVBox = self.mainVBox
        deck = self.deck
        ankiDeck = self.deckManager.get(deck.ankiDeckId)
        
        modesFrame = QGroupBox("(3) Choose Modes")
        
        mainVBox.modesBox = modesBox = QVBoxLayout()
        modesFrame.setLayout(modesBox)
        
        definitionBox = QHBoxLayout()
        
        self.defintionCB = defintionCB = QCheckBox("Definition Mode") 
        self.definitionCombo = definitionCombo = QComboBox()
        if deck.definitionField:
            defintionCB.setChecked(True)
        
        definitionCombo.setEnabled(deck.definitionField != None)
        definitionCombo.addItem("------------ Choose Definition field ------------")
        
        mw.connect(defintionCB, SIGNAL('clicked()'), self.enableDefinitionModes)
                
        allFields = list()
        for model in ankiDeck.models:
            for fieldModel in model.fieldModels:
                if fieldModel.name not in allFields:
                    allFields.append(fieldModel.name)
        allFields.sort()
        selectIndex = 0
        i = 1
        for fieldName in allFields:
            definitionCombo.addItem(fieldName)
            if fieldName == deck.definitionField:
                selectIndex = i
            i += 1
        definitionCombo.setCurrentIndex(selectIndex)
        
        self.definitionKeyCombo = definitionKeyCombo = QComboBox()
        definitionKeyCombo.setEnabled(deck.definitionField != None)
        definitionKeyCombo.addItem("---------- Choose Definition Key field ----------")
        
        selectIndex = 0
        i = 1
        for fieldName in allFields:
            definitionKeyCombo.addItem(fieldName)
            if fieldName == deck.definitionKeyField:
                selectIndex = i
            i += 1
        definitionKeyCombo.setCurrentIndex(selectIndex)
        
        definitionBox.addWidget(defintionCB)
        definitionBox.addWidget(definitionCombo)
        definitionBox.addWidget(definitionKeyCombo)
        
        modesBox.addLayout(definitionBox)
        
        mainVBox.addWidget(modesFrame)
        
        ankiDeck.close()
        
    def createField(self, fieldName, fieldDefaultValue, fieldEnabled):
        
        mmiLayout = QHBoxLayout()
        
        checkBox = QCheckBox(fieldName)
        checkBox.setChecked(fieldEnabled)
        
        mmiLayout.addWidget(checkBox)
        
        lineEdit = QLineEdit(fieldDefaultValue)
        lineEdit.setEnabled(fieldEnabled)
        mmiLayout.addWidget(lineEdit)
        
        mw.connect(checkBox, SIGNAL('clicked()'), lambda lx=lineEdit, cx=checkBox: lx.setEnabled(cx.isChecked()))
        
        self.fieldsComponents.append((checkBox, lineEdit))
        
        return mmiLayout
        
    def refreshPosOptions(self, deck, language):
        
        allPosListWidget = self.allPosListWidget
        allPosListWidget.clear()
        
        listAvailablePos = language.posOptions["availablePos"]
        listDisabledPos = deck.posOptions["disabledPos"]
        if listDisabledPos == None:
            listDisabledPos = list()
        
        for availablePos in listAvailablePos:
            if availablePos not in listDisabledPos:
                allPosListWidget.addItem(availablePos)
        
        bsPosListWidget = self.bsPosListWidget
        bsPosListWidget.clear()
        
        for disablePos in listDisabledPos:
            bsPosListWidget.addItem(disablePos)
        
    def setupPOSOptions(self):
        
        mainVBox = self.mainVBox
        deck  = self.deck
        language = deck.language
        
        optionsGroup = QGroupBox("(5) Choose Part Of Speech Options")
        
        mainVBox.posOptionsGrid = posOptionsBox = QHBoxLayout()
        optionsGroup.setLayout(posOptionsBox)
        
        self.allPosListWidget = allPosListWidget = QListWidget()
        allPosListWidget.setDragEnabled(True)
        allPosListWidget.setDropIndicatorShown(True)
        allPosListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        allPosListWidget.setAcceptDrops(True)
        allPosListWidget.setDragDropOverwriteMode(True)
        
        allPosListWidgetwithTitle = QVBoxLayout()
        allPosListWidgetwithTitle.addWidget(QLabel("Available Part Of Speech"))
        allPosListWidgetwithTitle.addWidget(allPosListWidget)
        posOptionsBox.addLayout(allPosListWidgetwithTitle)
        
        self.bsPosListWidget = bsPosListWidget = QListWidget()
        bsPosListWidget.setDragEnabled(True)
        bsPosListWidget.setDropIndicatorShown(True)
        bsPosListWidget.setDragDropMode(QAbstractItemView.DragDrop)
        bsPosListWidget.setAcceptDrops(True)
        bsPosListWidget.setDragDropOverwriteMode(True)

        bsPosListWidgetWithTitle = QVBoxLayout()
        bsPosListWidgetWithTitle.addWidget(QLabel("Disabled Part of Speech"))
        bsPosListWidgetWithTitle.addWidget(bsPosListWidget)
        posOptionsBox.addLayout(bsPosListWidgetWithTitle)
        
        mainVBox.addWidget(optionsGroup)
        
        if language:
            self.refreshPosOptions(deck, language)
        
    def setupOptions(self):
        
        mainVBox = self.mainVBox
        
        optionsGroup = QGroupBox("(6) Choose Maturity Options")
        
        mainVBox.fieldsGrid = matureGrid = QGridLayout()
        optionsGroup.setLayout(matureGrid)
        
        matureGrid.addWidget(QLabel("Mature"), 0, 1, Qt.AlignHCenter)
        matureGrid.addWidget(QLabel("Known"), 0, 2, Qt.AlignHCenter)
        matureGrid.addWidget(QLabel("Learn"), 0, 3, Qt.AlignHCenter)
        
        matureGrid.addWidget(QLabel("Maturity"), 1, 0)
        self.matureEdit = matureEdit = QLineEdit(str(self.deck.matureTreshold))
        matureGrid.addWidget(matureEdit, 1, 1)
        self.knownEdit = knownEdit = QLineEdit(str(self.deck.knownTreshold))
        matureGrid.addWidget(knownEdit, 1, 2)
        self.learnEdit = learnEdit = QLineEdit(str(self.deck.learnTreshold))
        matureGrid.addWidget(learnEdit, 1, 3)
        
        mainVBox.addWidget(optionsGroup)
        
    def setupButtons(self):
        
        mainVBox = self.mainVBox
        
        mainVBox.buttonBar = buttonBar = QBoxLayout(QBoxLayout.RightToLeft)
        
        cancelButton = QPushButton("Cancel")
        mw.connect(cancelButton, SIGNAL('clicked()'), self.closeWindows)
        buttonBar.addWidget(cancelButton)
        
        okButton = QPushButton("Ok")
        mw.connect(okButton, SIGNAL('clicked()'), self.controller.saveConfig)
        buttonBar.addWidget(okButton)
        
        mainVBox.addLayout(buttonBar)
        
    def chooseLanguage(self, idx):
        language = self.languagesService.getPredifinedLanguageByName(unicode(self.languageCombo.currentText()))
        self.refreshPosOptions(self.deck, language)
    
    def closeWindows(self):
        self.close()
