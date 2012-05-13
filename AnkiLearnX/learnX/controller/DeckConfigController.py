
#from anki.models import FieldModel
import anki.stdmodels

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class DeckConfigController:
    def __init__(self, interface):
        self.interface = interface
        self.parent = interface.parent
        self.deck = interface.deck
        
        self.deckManager = interface.deckManager
        
        self.decksService = self.parent.decksService
        
    def saveConfig(self):
        
        interface = self.interface
        
        if interface.languageCombo.currentIndex() <= 0:
            # Error : marked in red + Error message
            return
        if interface.expressionCombo.currentIndex() <= 0:
            # Error : marked in red + Error message
            return
        
        #if interface.defintionCB.isChecked() and interface.definitionCombo.currentIndex() <= 0:
            # Error : ...
        #    return
        
        mainVBox = interface.mainVBox
        deck = interface.deck
        realDeck = self.deckManager.get(deck.id)
        
        # Save Fields
        #for fieldsGrid in interface.fieldsComponents:
        #    
        #    isEnabled = fieldsGrid[0].isChecked()
        #    value = str(fieldsGrid[1].text())
        #    key = str(fieldsGrid[0].text())
        #    
        #    numeric = deck.fields[key][2]
        #
        #    models = realDeck.models
        #    
        #    deck.fields[key] = (value, isEnabled, numeric)
        #    
        #    if isEnabled:
        #        for model in models:
        #            
        #            field = FieldModel(unicode(value, "utf-8"), False, False)
        #            font = u"Arial"
        #            field.quizFontSize = 22
        #            field.quizFontFamily = font
        #            field.editFontSize = 20
        #            field.editFontFamily = font
        #            field.numeric = numeric

        #            log("add fields")
        #            try:
        #                fieldModelAlreadyAdded = False
        #                for fieldModel in model.fieldModels:
        #                    if fieldModel.name == value:
        #                        fieldModelAlreadyAdded = True
        #                        break
                            
        #                if not fieldModelAlreadyAdded:
        #                    realDeck.addFieldModel(model, field) 
        #            except Exception as e:
        #                log(e)
        #    else:
        #        for model in models:
        #            try:
        #                fieldToDelete = None
        #                for fieldModel in model.fieldModels:
        #                    if fieldModel.name == value:
        #                        fieldToDelete = fieldModel
        #                        break
        #                    
        #                if fieldToDelete != None:
        #                    realDeck.deleteFieldModel(model, fieldToDelete)
        #            except Exception as e:
        #                log(e)
        
        self.decksService.changeLanguage(interface.deck, unicode(interface.languageCombo.currentText()))
        
        deck.matureTreshold = int(str(interface.matureEdit.text()))
        deck.knownTreshold = int(str(interface.knownEdit.text()))
        deck.learnTreshold = int(str(interface.learnEdit.text()))
        deck.expressionField = str(interface.expressionCombo.currentText())
        
        bsPosListWidget = interface.bsPosListWidget
        disabledPosList = list()
        items = bsPosListWidget.findItems("*", Qt.MatchWrap | Qt.MatchWildcard)
        for item in items:
            log(item)
            disabledPosList.append(unicode(item.text()))
        deck.posOptions["disabledPos"] = disabledPosList
        
        #if interface.defintionCB.isChecked():
        #    deck.definitionField = str(interface.definitionCombo.currentText())
        #    if interface.definitionKeyCombo.currentIndex() > 0:
        #        deck.definitionKeyField = str(interface.definitionKeyCombo.currentText())
        #    else:
        #        deck.definitionKeyField = None
        
        self.decksService.updateDeck(deck)
        
        interface.parent.refreshAll()
        interface.close()
        