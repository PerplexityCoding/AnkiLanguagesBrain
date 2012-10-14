from languagesBrain.morphology.db.LanguagesBrainDB import *
from languagesBrain.morphology.db.dto.Note import *
from languagesBrain.morphology.db.dto.Morpheme import *

from languagesBrain.utils.Log import *

class NoteDao:
    def __init__(self):
        self.LanguagesBrainDB = LanguagesBrainDB.getInstance()
        
    def persistNotes(self, notes):
        
        db = self.LanguagesBrainDB.openDataBase()
        c = db.cursor()
        
        notesHash = dict()
        for note in notes:
            notesHash[note.id] = note
        
        c.execute("Select * From Notes Where id in (%s)" % ",".join(str(n.id) for n in notes))
        for row in c:
            notesHash.pop(row[0]).__init__(row[0], row[1], row[2], row[3])
        c.close()
        
        newNotes = set()
        if len(notesHash) > 0:
            c = db.cursor()
            for note in notesHash.values():
                 t = (note.id, note.lastUpdated, note.expressionCsum, note.score)
                 c.execute("Insert into Notes(id, last_updated, expression_csum, score)"
                           "Values (?,?,?,?)", t)
                 newNotes.add(note)
            db.commit()
            c.close()
        
        return newNotes, notes
    
    def updateNotes(self, notes):
        db = self.LanguagesBrainDB.openDataBase()    
        c = db.cursor()
        for note in notes:
            t = (note.lastUpdated, note.expressionCsum, note.score, note.id)
            c.execute("Update Notes Set last_updated = ?, expression_csum = ?, score = ? "
                      "Where id = ?", t)
        db.commit()
        c.close()
        
        return notes
    
    def selectNotes(self):
        
        db = self.LanguagesBrainDB.openDataBase()
        
        c = db.cursor()
        c.execute("Select * From Notes")
        
        notes = []
        for row in c:
            notes.append(Note(row[0], row[1], row[2], row[3]))
        c.close()
        
        return notes

