#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.utils.Log import *
from learnX.controller.DeckConfigController import *

from ankiqt import mw

class DeckConfig(QDialog):
    def __init__(self, deck, parent=None):
        super(DeckConfig, self).__init__(parent)
        
        self.parent = parent
        self.deck = deck
        self.setWindowTitle('Configure Deck Option')
        self.resize(600, 0)
        
        self.mainVBox = mainVBox = QVBoxLayout(self)
        self.controller = DeckConfigController(self)
                
        self.setupLanguages()        
        self.setupExpression()
        self.setupFields()
        self.setupOptions()
        self.setupButtons()
        
    def setupLanguages(self):
        mainVBox = self.mainVBox
        deck = self.deck
        mainVBox.chooseHbox = chooseHbox = QHBoxLayout()
        
        chooseHbox.addWidget(QLabel("   (1) Choose Language"))
        
        self.languageCombo = languageCombo = QComboBox()
        
        languagesNameAvailable = self.parent.languagesService.getAvailableLanguageName()
        #log(languagesName)

        currentIndex = 0
        languageCombo.addItem("------------------------")
        for languageName in languagesNameAvailable:
            languageCode = self.parent.languagesService.getCodeFromLanguageName(languageName)
            log(languageCode)
            log(deck.language)
            if deck.language != None and deck.language.nameId == languageCode:
                currentIndex = languageCombo.count()
            languageCombo.addItem(languageName)
        
        languageCombo.setCurrentIndex(currentIndex)
        
        chooseHbox.addWidget(languageCombo)
        mainVBox.addLayout(chooseHbox)
        
    def setupExpression(self):
        mainVBox = self.mainVBox
        
        expressionsFrame = QGroupBox("(2) Choose Expression")
        
        
        mainVBox.addWidget(expressionsFrame)
        
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
        
    def setupOptions(self):
        
        mainVBox = self.mainVBox
        
        optionsGroup = QGroupBox("(4) Choose Maturity Options")
        
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
        
    def closeWindows(self):
        self.close()
