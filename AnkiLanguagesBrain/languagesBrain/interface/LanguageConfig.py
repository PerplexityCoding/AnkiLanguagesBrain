#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from languagesBrain.utils.Log import *

from aqt import mw

class LanguageConfig(QDialog):
    def __init__(self, language, parent=None):
        super(LanguageChooser, self).__init__(parent)
        
        self.parent = parent
        self.setWindowTitle('Choose Language')
        self.resize(300, 0)
        
        self.mainVBox = mainVBox = QVBoxLayout(self)
        
        mainVBox.chooseHbox = chooseHbox = QHBoxLayout()
        
        chooseHbox.addWidget(QLabel("(1) Choose Language"))
        
        self.languageCombo = languageCombo = QComboBox()
       
        languageCombo.addItem(language.name)
            
        languageCombo.setCurrentIndex(0)
        languageCombo.setEnabled(False)
        
        chooseHbox.addWidget(languageCombo)
        
        mainVBox.buttonBar = buttonBar = QBoxLayout(QBoxLayout.RightToLeft)
        
        cancelButton = QPushButton("Cancel")
        mw.connect(cancelButton, SIGNAL('clicked()'), self.closeWindows)
        buttonBar.addWidget(cancelButton)
        
        okButton = QPushButton("Ok")
        mw.connect(okButton, SIGNAL('clicked()'), self.saveLanguage)
        buttonBar.addWidget(okButton)
        
        mainVBox.addLayout(chooseHbox)
        mainVBox.addLayout(buttonBar)
       
    def closeWindows(self):
        self.close()
        
    def saveLanguage(self):
        
        languageCombo = self.languageCombo
        #log(languageCombo.currentText())
        self.parent.languagesService.addLanguage(str(languageCombo.currentText()))
        
        self.parent.refreshAll()
        
        self.close()
    
    