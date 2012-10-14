from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Definition import *

class DefinitionDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
        
    def getDefinition(self, noteId):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (noteId,)
        c.execute("Select id, note_id, definition_hash, definition_key_hash From Definitions Where note_id = ?", t)
        
        row = c.fetchone()
        if row:
            definition = Definition(row[1], row[2], row[3], row[0])
            c.close()
        else:
            c.close()
            
            c = db.cursor()
            
            t = (noteId,)
            c.execute("Insert Into Definitions (note_id) Values (?)", t)
            db.commit()
            c.close()
            
            definition = Definition(noteId, None, None, -1)
            
            c = db.cursor()
            c.execute("Select id From Definitions Where note_id = ?", t)
            row = c.fetchone()
            if row:
                definition.id = row[0]
            c.close()        

        return definition
    
    def getDefinitions(self, notes):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        result = list()
        
        definitionToInsert = list()
        for note in notes:
            t = (note.id,)
            c.execute("Select id, note_id, definition_hash, definition_key_hash From Definitions Where note_id = ?", t)
            row = c.fetchone()
            if row:
                definition = Definition(row[1], row[2], row[3], row[0])
            else:
                definition = Definition(note.id, None, None, -1)
                definitionToInsert.append(definition)
            definition.note = note
            result.append(definition)
        c.close()
        
        c = db.cursor()
        for definition in definitionToInsert:
            t = (definition.note.id,)
            c.execute("Insert Into Definitions (note_id) Values (?)", t)
        db.commit()
        c.close()
                
        c = db.cursor()
        for definition in definitionToInsert:
            t = (definition.note.id,)
            c.execute("Select id From Definitions Where note_id = ?", t)
            row = c.fetchone()
            if row:
                definition.id = row[0]
        c.close()        

        return result
    
    
    def updateDefinitionMorphemes(self, definition, morphemes):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (definition.id,)
        c.execute("Delete From DefinitionsMorphemes Where definition_id = ?", t)
        
        db.commit()
        c.close()
        
        c = db.cursor()
        for morpheme in morphemes:
            t = (definition.id, morpheme.id)
            try:
                c.execute("Insert Into DefinitionsMorphemes(definition_id, morpheme_id) Values(?,?)", t)
            except Exception: pass
        db.commit()
        c.close()
        
    def updateAllDefinitionsMorphemes(self, definitions):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        for definition in definitions:
            t = (definition.id,)
            c.execute("Delete From DefinitionsMorphemes Where definition_id = ?", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        for definition in definitions:
            for morpheme in definition.definitionMorphemes:
                t = (definition.id, morpheme.id)
                try:
                    c.execute("Insert Into DefinitionsMorphemes(definition_id, morpheme_id) Values(?,?)", t)
                except Exception: pass
        db.commit()
        c.close()
        
    def updateDefinitionKeyMorphemes(self, definition, morphemes):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (definition.id,)
        c.execute("Delete From DefinitionsKeysMorphemes Where definition_id = ?", t)
        
        db.commit()
        c.close()
        
        c = db.cursor()
        for morpheme in morphemes:
            t = (definition.id, morpheme.id)
            try:
                 c.execute("Insert Into DefinitionsKeysMorphemes(definition_id, morpheme_id) Values(?,?)", t)
            except Exception: pass
        db.commit()
        c.close()
        
    def updateAllDefinitionsKeysMorphemes(self, definitions):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        for definition in definitions:
            t = (definition.id,)
            c.execute("Delete From DefinitionsKeysMorphemes Where definition_id = ?", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        for definition in definitions:
            for morpheme in definition.definitionMorphemesKey:
                t = (definition.id, morpheme.id)
                try:
                     c.execute("Insert Into DefinitionsKeysMorphemes(definition_id, morpheme_id) Values(?,?)", t)
                except Exception: pass
        db.commit()
        c.close()
        
    def getAllDefinitionMorphemes(self, definition):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (definition.id,)
        c.execute("Select morpheme_id From DefinitionsMorphemes Where definition_id = ?", t)
        
        morphemesId = list()
        for row in c:
            morphemesId.append(row[0])
        
        db.commit()
        c.close()
        
        return morphemesId
    
    def getAllDefinitionKeyMorphemes(self, definition):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (definition.id,)
        c.execute("Select morpheme_id From DefinitionsKeysMorphemes Where definition_id = ?", t)
        
        morphemesId = list()
        for row in c:
            morphemesId.append(row[0])
        
        db.commit()
        c.close()
        
        return morphemesId
    
    def update(self, definition):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (definition.definitionHash, definition.definitionKeyHash, definition.id)
        c.execute("Update Definitions Set definition_hash = ?, definition_key_hash = ? Where id = ?", t)
        
        db.commit()
        c.close()
        
    def updateAll(self, definitions):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        for definition in definitions:
            t = (definition.definitionHash, definition.definitionKeyHash, definition.id)
            c.execute("Update Definitions Set definition_hash = ?, definition_key_hash = ? Where id = ?", t)
        
        db.commit()
        c.close()