from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Note import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *

class NoteDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
        
    def persistNotes(self, notes):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        toInsert = list()
        for note in notes:
            t = (note.id, )
            c.execute("Select * From Notes Where id = ?", t)
            
            row = c.fetchone()
            if row:
                note.__init__(row[0], row[1], row[2], row[3], row[4])
            else:
                toInsert.append(note)
        c.close()
        
        if len(toInsert) > 0:
            c = db.cursor()
            for note in toInsert:
                 t = (note.id, note.lastUpdated, note.expressionCsum, note.changed, note.score)
                 c.execute("Insert into Notes(id, last_updated, expression_csum, changed, score)"
                           "Values (?,?,?,?,?)", t)
            db.commit()
            c.close()
        
        return notes
    
    def updateNotes(self, notes):
        db = self.learnXdB.openDataBase()    
        c = db.cursor()
        for note in notes:
            t = (note.lastUpdated, note.expressionCsum, note.changed, note.score, note.id)
            c.execute("Update Notes Set last_updated = ?, expression_csum = ?, changed = ?, score = ? "
                      "Where id = ?", t)
        db.commit()
        c.close()
        
        return notes
    
    def selectNotes(self):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("Select * From Notes")
        
        notes = []
        for row in c:
            notes.append(Note(row[0], row[1], row[2], row[3], row[4]))
        c.close()
        
        return notes
        