﻿#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.utils.Log import *

from ankiqt import mw
from anki.models import Model, CardModel, FieldModel

from learnX.morphology.service.LanguagesService import *
from learnX.morphology.db.dto.Deck import *

from learnX.utils.AnkiHelper import *

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
        realDeck = AnkiHelper.getDeck(deck.path)
        
        # Save Fields
        for fieldsGrid in self.fieldsComponents:
            
            isEnabled = fieldsGrid[0].isChecked()
            value = str(fieldsGrid[1].text())
            key = str(fieldsGrid[0].text())
            
            numeric = deck.fields[key][2]

            models = realDeck.models
            
            deck.fields[key] = (value, isEnabled, numeric)
            
            if isEnabled:
                for model in models:
                    
                    field = FieldModel(unicode(value, "utf-8"), False, False)
                    font = u"Arial"
                    field.quizFontSize = 22
                    field.quizFontFamily = font
                    field.editFontSize = 20
                    field.editFontFamily = font
                    field.numeric = numeric

                    log("add fields")
                    try:
                        fieldModelAlreadyAdded = False
                        for fieldModel in model.fieldModels:
                            if fieldModel.name == value:
                                fieldModelAlreadyAdded = True
                                break
                            
                        if not fieldModelAlreadyAdded:
                            realDeck.addFieldModel(model, field) 
                    except Exception as e:
                        log(e)
            else:
                for model in models:
                    try:
                        fieldToDelete = None
                        for fieldModel in model.fieldModels:
                            if fieldModel.name == value:
                                fieldToDelete = fieldModel
                                break
                            
                        if fieldToDelete != None:
                            realDeck.deleteFieldModel(model, fieldToDelete)
                    except Exception as e:
                        log(e)
        
        deck.matureTreshold = str(self.matureEdit.text())
        deck.knownTreshold = str(self.knownEdit.text())
        deck.learnTreshold = str(self.learnEdit.text())
        
        self.parent.decksService.changeLanguage(self.deck, str(self.languageCombo.currentText()))
        
        realDeck.save()
        realDeck.close()
        
        self.parent.refreshAll()
        self.close()
