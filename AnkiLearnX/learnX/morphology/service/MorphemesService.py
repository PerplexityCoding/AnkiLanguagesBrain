
from learnX.morphology.db.dao.MorphemeLemmeDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.NoteDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.DeckDao import *
from learnX.morphology.db.dao.DefinitionDao import *

from learnX.morphology.db.dto.Card import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *
from learnX.utils.Utils import *
from learnX.utils.KanjiHelper import *

from learnX.morphology.lemmatizer.cst.CstLemmatizer import *

class MorphemesService:
    
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        
        self.lemmeDao = MorphemeLemmeDao()
        self.morphemeDao = MorphemeDao()
        self.noteDao = NoteDao()
        self.cardDao = CardDao()
        self.deckDao = DeckDao()
        self.definitionDao = DefinitionDao()
    
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
        self.notesService = self.serviceLocator.getNotesService()


    def extractMorphemes(self, expression, deck, language):
        morphemes = language.posTagger.posMorphemes(expression, deck, language)
        return morphemes
    
    def analyzeLemmes(self, notes, deck, language):
    
        # Unique Morphemes
        log("Extract Morphemes")
        allUniqueMorphLemmes = dict()
        for note in notes:
            morphLemmes = self.extractMorphemes(note.ankiNote[deck.expressionField], deck, language)
            noteMorphLemmes = list()
            for morphLemme in morphLemmes:
                if morphLemme in allUniqueMorphLemmes:
                    morphLemme = allUniqueMorphLemmes[morphLemme]
                else:
                    allUniqueMorphLemmes[morphLemme] = morphLemme
                noteMorphLemmes.append(morphLemme)
            note.morphLemmes = noteMorphLemmes
        
        allUniqueMorphLemmes = self.getList(allUniqueMorphLemmes)
        
        log("Lemmatize Morphemes : " + str(len(allUniqueMorphLemmes)))
        if language.lemmatizer:
            language.lemmatizer.lemmatizeMorphemes(allUniqueMorphLemmes)
        
        self.filterMorphLemmes(allUniqueMorphLemmes)
        
        self.rankMorphLemmes(allUniqueMorphLemmes)
        
        log("persist All Lemmes")
        self.lemmeDao.persistLemmes(allUniqueMorphLemmes)
    
    def analyzeMorphemes(self, notes, deck, language):
        
        log("Compute Notes <-> Morphemes")
        allMorphemes = list()
        for note in notes:
            noteUniqueMorphemes = list()
            for morphLemme in note.morphLemmes:
                morpheme = Morpheme(note.id, 0, False, morphLemme.id, -1)
                if morpheme not in noteUniqueMorphemes:    
                    noteUniqueMorphemes.append(morpheme)
                    allMorphemes.append(morpheme)
            note.expressionCsum = Utils.fieldChecksum(note.ankiNote[deck.expressionField])
            note.lastUpdated = note.ankiNote.mod
            note.ankiNote = None
        
        log("persist All Morphemes")
        self.morphemeDao.persistMorphemes(allMorphemes)
        
        log("update All")
        self.noteDao.updateNotes(notes) 
        
        for note in notes:
            note.morphLemmes = None
    
    def getList(self, dict):
        dictList = list()
        for key, value in dict.iteritems():
            dictList.append(value)
        return dictList
    
    # XXX: on considère qu'il y a une seul carte par note ! pour le moment
    def refreshInterval(self, modifiedCards):
        
        for card in modifiedCards:
            card.interval = card.ankiCard.ivl
            
        self.cardDao.updateCards(modifiedCards)
        self.morphemeDao.updateInterval(modifiedCards)
        
    
    # Store temporarly (not in database) definition morphemes and score in notes
    # Dont work with lemmatizater
    def getMorphemesFromDB(self, expression, deck, language):
        
        # Unique Morphemes
        log("Extract Morphemes")
        morphLemmes = self.extractMorphemes(expression, deck, language)
        noteMorphemes = list()
        for morphemeLemme in morphLemmes:
            morphLemmeDB = self.lemmeDao.findById(morphemeLemme.id)
            if morphLemmeDB == None:
                morpheme = Morpheme(-1, 0, None, 0, -1)
                morpheme.morphLemme = morphemeLemme
            else:
                morpheme = self.morphemeDao.findByLemmeId(morphLemmeDB.id)
                if morpheme == None:
                    continue
                morpheme.morphLemme = morphLemmeDB
            if morpheme not in noteMorphemes:
                noteMorphemes.append(morpheme)
        return noteMorphemes
    
    def analyseDefinition(self, deck, language, notes, ankiNotes):
        
        definitions = self.definitionDao.getDefinitions(notes)
        
        modifiedDefinition = list()
        keyModifiedDefinition = list()
        defModifiedDefinition = list()
        
        for definition in definitions:
            note = definition.note
            if note.ankiLastModified == note.lastUpdated:
                continue
            
            isModified = False
            definitionExpression = ankiNotes[note.ankiNoteIndex][deck.definitionField]
            if definition.definitionHash == None or int(definition.definitionHash) != hash(definitionExpression):
                definition.definitionMorphemes = self.getMorphemesFromDB(definitionExpression, deck, language)
                definition.definitionHash = hash(definitionExpression)
                defModifiedDefinition.append(definition)
                isModified = True
            
            definitionKeyExpression = ankiNotes[note.ankiNoteIndex][deck.definitionKeyField]
            if definition.definitionKeyHash == None or int(definition.definitionKeyHash) != hash(definitionKeyExpression):
                definition.definitionMorphemesKey = self.getMorphemesFromDB(definitionKeyExpression, deck, language)
                definition.definitionKeyHash = hash(definitionKeyExpression)
                keyModifiedDefinition.append(definition)
                isModified = True
            
            if isModified == True:
                modifiedDefinition.append(definition)
        
        if len(defModifiedDefinition) > 0:
            self.definitionDao.updateAllDefinitionsMorphemes(defModifiedDefinition)
        if len(keyModifiedDefinition) > 0:
            self.definitionDao.updateAllDefinitionsKeysMorphemes(keyModifiedDefinition)
        if len(modifiedDefinition) > 0:
            self.definitionDao.updateAll(modifiedDefinition)
    
    def getMorphemesDefinition(self, definition):
        morphemesId = self.definitionDao.getAllDefinitionMorphemes(definition)
        
        morphemes = list()
        for morphemeId in morphemesId:
            morpheme = self.morphemeDao.findMorphemeById(morphemeId)
            if morpheme:
                morpheme.morphLemme = self.lemmeDao.findById(morpheme.morphLemmeId)
                if morpheme.morphLemme:
                    morphemes.append(morpheme)
            
        return morphemes
    
    def getMorphemesDefinitionKey(self, definition):
        morphemesId = self.definitionDao.getAllDefinitionKeyMorphemes(definition)
        
        morphemes = list()
        for morphemeId in morphemesId:
            morpheme = self.morphemeDao.findMorphemeById(morphemeId)
            if morpheme:
                morpheme.morphLemme = self.lemmeDao.findById(morpheme.morphLemmeId)
                if morpheme.morphLemme:
                    morphemes.append(morpheme)
        return morphemes
    
    def getAllPOS(self, language):
        try:
            return language.posOptions["activatedPos"]
        except Exception: pass
  
    def getAllSubPOS(self, language):
        try:
            return language.posOptions["activatedSubPos"]
        except Exception: pass
    
    def getLemmesFromNote(self, note):
        return self.lemmeDao.getLemmesFromNote(note)
    
    def getMorphemes(self, searchText = None, decksId = None):
        
        if searchText == None or searchText == "":
            return self.lemmeDao.getMorphemes(decksId)
        else:
            searchExpressions = searchText.split(" ")
            status_changed = None
            status = None
            pos = None
            subPos = None
            expressions = []
            
            for searchExpression in searchExpressions:
                uni = unicode(searchExpression)
                if searchExpression == "is:changed":
                    status_changed = True
                elif searchExpression == "-is:changed":
                    status_changed = False
                elif searchExpression == "status:None":
                    status = Morpheme.STATUS_NONE
                elif searchExpression == "status:Learnt":
                    status = Morpheme.STATUS_LEARNT
                elif searchExpression == "status:Known":
                    status = Morpheme.STATUS_KNOWN
                elif searchExpression == "status:Mature":
                    status = Morpheme.STATUS_MATURE
                elif uni.startswith("pos:"):
                    pos = uni.split(":")[1]                    
                elif uni.startswith("sub_pos:"):
                    subPos = uni.split(":")[1]
                else:
                    expressions.append(uni)
            return self.lemmeDao.getMorphemes(decksId, expressions, status, status_changed, pos, subPos)