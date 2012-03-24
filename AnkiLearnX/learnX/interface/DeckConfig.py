#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.utils.Log import *

from ankiqt import mw

from learnX.morphology.service.LanguagesService import *

class DeckConfig(QDialog):
    def __init__(self, deck, parent=None):
        super(DeckConfig, self).__init__(parent)
        
        self.parent = parent
        self.deck = deck
        self.setWindowTitle('Configure Deck Option')
        self.resize(600, 0)
        
        self.mainVBox = mainVBox = QVBoxLayout(self)
        
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
        
        self.setupFields()
        
        self.setupOptions()
        
        mainVBox.buttonBar = buttonBar = QBoxLayout(QBoxLayout.RightToLeft)
        
        cancelButton = QPushButton("Cancel")
        mw.connect(cancelButton, SIGNAL('clicked()'), self.closeWindows)
        buttonBar.addWidget(cancelButton)
        
        okButton = QPushButton("Ok")
        mw.connect(okButton, SIGNAL('clicked()'), self.saveConfig)
        buttonBar.addWidget(okButton)
        mainVBox.addLayout(buttonBar)
        
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
        
    def setupFields(self):
        
        mainVBox = self.mainVBox
        
        fieldsFrame = QGroupBox("(2) Choose Fields")
        
        mainVBox.fieldsGrid = fieldsGrid = QGridLayout()
        fieldsFrame.setLayout(fieldsGrid)
        
        fieldsGrid.setHorizontalSpacing(25)
        
        self.fieldsComponents = []
        if self.deck.fields:
            i = 0
            j = 0
            for field in self.deck.fields:
                fieldsGrid.addLayout(self.createField(field[0], field[1], field[2]), j, i)
                i += 1
                if i == 3:
                    i = 0
                    j += 1
        
        mainVBox.addWidget(fieldsFrame)
        
    def setupOptions(self):
        
        mainVBox = self.mainVBox
        
        optionsGroup = QGroupBox("(3) Choose Options")
        
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
        
    def closeWindows(self):
        self.close()

    def saveConfig(self):
        
        if self.languageCombo.currentIndex() <= 0:
            # Error
            return
        
        mainVBox = self.mainVBox
        deck = self.deck
        
        # Save Fields
        fields = []
        for fieldsGrid in self.fieldsComponents:
            fields.append((str(fieldsGrid[0].text()), str(fieldsGrid[1].text()), fieldsGrid[0].isChecked()))
        deck.fields = fields
        
        deck.matureTreshold = str(self.matureEdit.text())
        deck.knownTreshold = str(self.knownEdit.text())
        deck.learnTreshold = str(self.learnEdit.text())
        
        #Add / Delete Fields To Deck if not Present
        
        self.parent.decksService.changeLanguage(self.deck, str(self.languageCombo.currentText()))
        self.parent.refreshAll()
        self.close()
