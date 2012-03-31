
from learnX.morphology.service.Mecab import *
from learnX.morphology.service.FactsService import *
from learnX.morphology.service.DecksService import *
from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.MorphemesService import *

class ServicesLocator:
    
    instance = None
    
    def __init__(self, useGetInstanceInstead):
        self.factsService = FactsService(self)
        self.decksService = DecksService(self)
        self.languagesService = LanguagesService(self)
        self.morphemesService = MorphemesService(self)
        ServicesLocator.instance = self
        
        self.factsService.setupServices()
        self.decksService.setupServices()
        self.languagesService.setupServices()
        self.morphemesService.setupServices()
    
    @staticmethod
    def getInstance():
        if ServicesLocator.instance == None:
            ServicesLocator.instance = ServicesLocator(None)
        return ServicesLocator.instance

    def getFactsService(self):
        return self.factsService
    
    def getDecksService(self):
        return self.decksService
    
    def getLanguagesService(self):
        return self.languagesService
    
    def getMorphemesService(self):
        return self.morphemesService
    
    