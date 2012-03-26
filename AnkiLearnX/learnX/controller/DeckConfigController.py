
from anki.models import FieldModel

from learnX.utils.AnkiHelper import *


class DeckConfigController:
    def __init__(self, interface):
        self.interface = interface
        self.parent = interface.parent
        self.deck = interface.deck
        
        self.decksService = self.parent.decksService
        
    def saveConfig(self):
        
        interface = self.interface
        
        if interface.languageCombo.currentIndex() <= 0:
            # Error
            return
        
        mainVBox = interface.mainVBox
        deck = interface.deck
        realDeck = AnkiHelper.getDeck(deck.path)
        
        # Save Fields
        for fieldsGrid in interface.fieldsComponents:
            
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
        
        deck.matureTreshold = str(interface.matureEdit.text())
        deck.knownTreshold = str(interface.knownEdit.text())
        deck.learnTreshold = str(interface.learnEdit.text())
        
        self.decksService.changeLanguage(interface.deck, str(interface.languageCombo.currentText()))
        
        realDeck.save()
        realDeck.close()
        
        interface.parent.refreshAll()
        interface.close()