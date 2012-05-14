#-*- coding: utf-8 -*-

from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.MorphemeLemme import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *
from learnX.utils.Utils import *

class MorphemeLemmeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistAll(self, lemmes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        lemmesToInsert = list()
        for lemme in lemmes:
            
            t = (lemme.id,)
            c.execute("Select id From MorphemeLemmes Where id = ?", t)            
            lemmeId = c.fetchone()
            if lemmeId == None:
                lemmesToInsert.append(lemme)
        c.close()
            
        c = db.cursor()
        for lemme in lemmesToInsert:
            t = (lemme.id, lemme.pos, lemme.subPos, lemme.read, lemme.base, lemme.rank,
                 lemme.maxInterval, lemme.score)
            c.execute("Insert into MorphemeLemmes(id, pos, sub_pos, read, base, rank, max_interval, score) "
                      "Values (?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
            
        return lemmes
    
    def updateAllRank(self, lemmes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c = db.cursor()
        for lemme in lemmes:
            t = (lemme.rank, lemme.id)
            c.execute("Update MorphemeLemmes set rank = ? Where id = ?", t)
        db.commit()
        c.close()
            
        return lemmes
    
    def updateAllScore(self, lemmes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c = db.cursor()
        for lemme in lemmes:
            t = (lemme.score, lemme.id)
            c.execute("Update MorphemeLemmes set score = ? Where id = ?", t)
        db.commit()
        c.close()
            
        return lemmes
    
    def findById(self, id):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (id,)
        c.execute("Select id, base, pos, sub_pos, read, rank, max_interval, score From MorphemeLemmes Where id = ?", t)
        
        row = c.fetchone()
        if row:
            morpheme = MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[0])
            c.close()
            return morpheme
        return None
    
    def getAll(self):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select id, base, pos, sub_pos, read, rank, max_interval, score From MorphemeLemmes")

        morphemes = list()
        for row in c:
            morphemes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[0]))
        c.close()
        
        return morphemes
    
    def getKnownLemmesIntervalDB(self):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select base, read, max_interval From MorphemeLemmes where max_interval > 0")
        intervalDb = dict()
        for row in c:
           intervalDb[(row[0], row[1])] = row[2]
        c.close()
        return intervalDb
        
    def getLemmesFromNote(self, note):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (note.id,)
        c.execute("Select ml.id, base, pos, sub_pos, read, rank, max_interval, ml.score "
                  "From MorphemeLemmes ml, Morphemes m "
                  "Where ml.id = m.morph_lemme_id and m.note_id = ?", t)
        lemmes = list()
        for row in c:
           lemmes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[0]))
        c.close()
        
        return lemmes
        
    def getLemmeIntervalFromNote(self, note):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (note.id,)
        c.execute("Select max_interval, score From MorphemeLemmes ml, Morphemes m "
                  "Where ml.id = m.morph_lemme_id and m.note_id = ?", t)
        lemmes = list()
        for row in c:
           lemmes.append((row[0], row[1]))
        c.close()
        
        return lemmes

    def getMorphemes(self, decksId = None, expressions = None, status = None, status_changed = None, pos = None, subPos = None):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "Select base, pos, sub_pos, read, m.id, m.changed, m.interval, mm.id, count(fm.note_id) as c, m.score "
        sql += "From Morphemes m, NotesMorphemes fm, MorphemeLemmes mm, Notes f "
        
        if decksId != None:
            sql += ", Decks d "
        
        sql += "Where mm.id = m.morph_lemme_id and m.id = fm.morpheme_id and f.id = fm.note_id "
        
        if decksId != None:
            sql += "and d.id = f.deck_id "
        
        t = list()
        if expressions != None:
            for expression in expressions:
                sql += " and (mm.base like ? or mm.read like ?) " 
                t.append("%" + expression + "%")
                t.append("%" + expression + "%")
        if status != None:
            sql += "and m.status = ? " 
            t.append(status)
        if status_changed != None:
            sql += "and m.status_changed = ? " 
            if status_changed:
                t.append(1)
            else:
                t.append(0)
        if pos != None:
            sql += "and pos = ? "
            t.append(pos)
        if subPos != None:
            sql += "and sub_pos = ? "
            t.append(subPos)
        if decksId != None and len(decksId) > 0:
            sql += "and ("
            i = 1
            for deckId in decksId:
                t.append(deckId)
                sql += "d.id = ?"
                if i < len(decksId):
                    sql += " or "
                i += 1
            sql += ")"
        
        sql += " group by m.id"
        
        log("getMorphemes SQL Start")
        log(sql)
        log(t)
        if len(t) > 0:
            c.execute(sql, t)
        else:
            c.execute(sql)
        log("getMorphemes SQL End")
        
        log("getMorphemes get Result Start")
        morphemes = []
        for row in c:
            morphemeLemme = MorphemeLemme(row[0], None, row[1], row[2], row[3], row[4])
            morpheme = Morpheme(row[5], row[6], row[7], morphemeLemme, row[9], row[4])
            morpheme.notesCount = row[8]
            morphemes.append(morpheme)
        log("getMorphemes get Result End")
        
        c.close()
        
        return morphemes

        