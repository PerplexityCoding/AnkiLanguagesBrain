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
                note.__init__(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            else:
                toInsert.append(note)
        c.close()
        
        c = db.cursor()
        for note in toInsert:
             t = (note.id, note.lastUpdated, note.expressionCsum, note.morphemesChanged, note.status, note.statusChanged, note.score)
             c.execute("Insert into Notes(id, last_updated, expression_csum, morphemes_changed, status, status_changed, score)"
                       "Values (?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        return notes
    
    def insert(self, note):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        if note.deck:
            note.deckId = note.deck.id
        
        t = (note.ankiNoteId, note.lastUpdated, note.expressionCsum, note.morphemesChanged, note.status, note.statusChanged, note.score)
        c.execute("Insert into Notes(anki_note_id, last_updated, expression_csum, morphemes_changed, status, status_changed, score)"
                  "Values (?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        
        t = (note.deckId, note.ankiNoteId)
        c.execute("Select id From Notes Where deck_id = ? and anki_note_id = ?", t)
        
        for row in c:
            note.id = row[0]
        
        c.close()
    
        return note
    
    def insertAll(self, notes):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for note in notes:
            if note.deck:
                note.deckId = note.deck.id
            
            t = (note.deckId, note.ankiNoteId, note.lastUpdated, note.expressionCsum, note.morphemesChanged, note.status, note.statusChanged, note.score)
            c.execute("Insert into Notes(deck_id, anki_note_id, last_updated, expression_csum, morphemes_changed, status, status_changed, score)"
                      "Values (?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        
        for note in notes:
            t = (note.deckId, note.ankiNoteId)
            c.execute("Select id From Notes Where deck_id = ? and anki_note_id = ?", t)
            
            for row in c:
                note.id = row[0]
        
        c.close()
    
    def update(self, note):
        
        db = self.learnXdB.openDataBase()    
        c = db.cursor()
        
        t = (note.lastUpdated, note.expressionCsum, note.morphemesChanged, note.status,
             note.statusChanged, note.score, note.id)
        c.execute("Update Notes Set last_updated = ?, expression_csum = ?, morphemes_changed = ?,"
                  "status = ?, status_changed = ?, score = ? "
                  "Where id = ?", t)
        db.commit()
        c.close()
        
        return note

    def updateAll(self, notes):
        db = self.learnXdB.openDataBase()    
        c = db.cursor()
        for note in notes:
            t = (note.lastUpdated, note.expressionCsum, note.morphemesChanged, note.status,
                 note.statusChanged, note.score, note.id)
            c.execute("Update Notes Set last_updated = ?, expression_csum = ?, morphemes_changed = ?,"
                      "status = ?, status_changed = ?, score = ? "
                      "Where id = ?", t)
        db.commit()
        c.close()
        
        return notes
    
    def findById(self, noteId):
    
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        t = (noteId,)
        c.execute("Select * From Notes Where id = ?", t)
        
        note = None
        for row in c:
            note = Note(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0])

        c.close()
        
        return note
    
    
    def findByChangedMorphemes(self, decksId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        sql = "Select distinct f.id, f.deck_id, f.anki_note_id, f.last_updated, f.expression_csum, "
        sql += "f.morphemes_changed, f.status, f.status_changed, f.score "
        sql += "From Morphemes m, NotesMorphemes mf, Notes f "
        sql += "Where mf.morpheme_id = m.id and f.id = mf.note_id and m.status_changed = 1 "
        
        t = []
        if decksId != None and len(decksId) > 0:
            sql += "and ("
            i = 1
            for deckId in decksId:
                t.append(deckId)
                sql += "f.deck_id = ?"
                if i < len(decksId):
                    sql += " or "
                i += 1
            sql += ")"
        
        if len(t) > 0:
            c.execute(sql, t)
        else:
            c.execute(sql)
        
        notes = []
        for row in c:
            notes.append(Note(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]))
        
        c.close()
        
        return notes
    
    def selectAll(self):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("Select * From Notes")
        
        notes = []
        for row in c:
            notes.append(Note(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        c.close()
        
        return notes
        
    
    def insertNoteMorphemes(self, note, morphemes):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (note.id,)
        c.execute("Delete From NotesMorphemes Where note_id = ?", t)
        
        db.commit()
        c.close()
        
        c = db.cursor()
        for morpheme in morphemes:
            t = (note.id, morpheme.id)
            c.execute("Insert Into NotesMorphemes(note_id, morpheme_id) Values(?,?)", t)
        db.commit()
        c.close()
    
    def clearAllNotesStatus(self, decksId):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "Update Notes Set status_changed = 0 "

        t = []
        if decksId != None and len(decksId) > 0:
            sql += " Where "
            i = 1
            for deckId in decksId:
                t.append(deckId)
                sql += "deck_id = ?"
                if i < len(decksId):
                    sql += " or "
                i += 1
        
        if len(t) > 0:
            c.execute(sql, t)
        else:
            c.execute(sql)

        db.commit()
        c.close()
        