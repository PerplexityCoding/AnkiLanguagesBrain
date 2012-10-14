
from learnX.morphology.service.NotesService import *
from learnX.morphology.service.DecksService import *
from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.MorphemesService import *

from learnX.morphology.db.dto.Language import *

from learnX.morphology.service.morphemes.JapaneseMorphemesService import *
from learnX.morphology.service.morphemes.FrenchMorphemesService import *

class ServicesLocator:
    
    instance = None
    
    def __init__(self, useGetInstanceInstead):
        self.notesService = NotesService(self)
        self.decksService = DecksService(self)
        self.languagesService = LanguagesService(self)
        self.morphemesService = MorphemesService(self)
        self.japaneseMorphemesService = JapaneseMorphemesService(self)
        self.frenchMorphemesService = FrenchMorphemesService(self)
        
        ServicesLocator.instance = self
        
        self.notesService.setupServices()
        self.decksService.setupServices()
        self.languagesService.setupServices()
        self.morphemesService.setupServices()
        self.japaneseMorphemesService.setupServices()
        self.frenchMorphemesService.setupServices()
    
    @staticmethod
    def getInstance():
        if ServicesLocator.instance == None:
            ServicesLocator.instance = ServicesLocator(None)
        return ServicesLocator.instance

    def getNotesService(self):
        return self.notesService
    
    def getDecksService(self):
        return self.decksService
    
    def getLanguagesService(self):
        return self.languagesService
    
    def getMorphemesService(self, language = None):
        
        if language != None:
            if language.nameId == Language.JAPANESE:
                return self.japaneseMorphemesService
            elif language.nameId == Language.FRENCH:
                return self.frenchMorphemesService
        return self.morphemesService
    
    