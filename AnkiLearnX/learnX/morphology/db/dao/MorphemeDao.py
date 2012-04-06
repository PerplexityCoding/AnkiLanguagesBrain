from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.MorphemeLemme import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *

import math

class MorphemeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistAll(self, morphemes):
        db = self.learnXdB.openDataBase()
        
        morphemesToInsert = []
        c = db.cursor()
        
        for morpheme in morphemes:
            if morpheme.morphLemme:
                morpheme.morphLemmeId = morpheme.morphLemme.id
            t = (morpheme.morphLemmeId,)
            c.execute("Select id, status, status_changed, score From Morphemes Where morph_lemme_id = ?", t)
            row = c.fetchone()
            if row:
                morpheme.id = row[0]
                morpheme.status = row[1]
                morpheme.statusChanged = row[2]
                morpheme.score = row[3]
            else:
                morphemesToInsert.append(morpheme)
        c.close()
        
        c = db.cursor()
        for morpheme in morphemesToInsert:
            t = (morpheme.status, morpheme.statusChanged, morpheme.morphLemmeId, morpheme.score)
            c.execute("Insert into Morphemes(status, status_changed, morph_lemme_id, score) "
                      "Values (?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        for morpheme in morphemesToInsert:
            t = (morpheme.morphLemmeId,)
            c.execute("Select id From Morphemes Where morph_lemme_id = ?", t)
            for row in c:
                morpheme.id = row[0]
        c.close()
    
        return morphemes    
    
    def persist(self, morpheme):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        if morpheme.morphLemme:
            morpheme.morphLemmeId = morpheme.morphLemme.id
        
        t = (morpheme.morphLemmeId,)
        c.execute("Select id, status, status_changed From Morphemes Where morph_lemme_id = ?", t)
        
        row = c.fetchone()
        if morphemeInfo:
            morpheme.id = row[0]
            morpheme.status = row[1]
            morpheme.statusChanged = row[2]
            return morpheme
        else:
            c.close()
            
            c = db.cursor()
            t = (morpheme.status, morpheme.statusChanged, morpheme.morphLemmeId, morpheme.score)
            c.execute("Insert into Morphemes(status, status_changed, morph_lemme_id, score) "
                      "Values (?,?,?,?)", t)
            db.commit()
            c.close()
            
            c = db.cursor()
            
            c.execute("Select count(*) From MorphemeLemmes")
            for row in c:
                morpheme.id = row[0] - 1
            c.close()
        
        return morpheme

    def updateAll(self, morphemes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        for morpheme in morphemes:
            t = (morpheme.status, morpheme.statusChanged, morpheme.morphLemmeId, morpheme.score, morpheme.id)
            c.execute("Update Morphemes Set status = ?, status_changed = ?, morph_lemme_id = ?, score = ? Where id = ?", t)
        
        db.commit()
        c.close()
    
        return morphemes

    def getNewStatus(self, morpheme):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "Select c.id from Cards c, Facts f, FactsMorphemes fm "
        sql += "Where c.fact_id = f.id and f.id = fm.fact_id and fm.morpheme_id = ? and c.status = ? limit 1"
        
        t = (morpheme.id, Card.STATUS_MATURE)
        c.execute(sql, t)
        row = c.fetchone()
        if row:
            c.close()
            return Morpheme.STATUS_MATURE
        c.close()
        
        c = db.cursor()
        t = (morpheme.id, Card.STATUS_KNOWN)
        c.execute(sql, t)
        row = c.fetchone()
        if row:
            c.close()
            return Morpheme.STATUS_KNOWN
        c.close()
        
        c = db.cursor()
        t = (morpheme.id, Card.STATUS_LEARNT)
        c.execute(sql, t)
        row = c.fetchone()
        if row:
            c.close()
            return Morpheme.STATUS_LEARNT
        c.close()
        
        return Morpheme.STATUS_NONE
        
    def getMorphemesFromCard(self, card):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (card.id,)
        c.execute("Select m.id, m.status, m.status_changed, m.morph_lemme_id, m.score "
                  "From Morphemes m, FactsMorphemes mf, Cards c "
                  "Where mf.morpheme_id = m.id and mf.fact_id = c.fact_id and c.id = ?", t)
        morphemes = []
        for row in c:
            morphemes.append(Morpheme(row[1], row[2], row[3], None, row[4], row[0]))
            
        c.close()
        
        return morphemes
    
    def getMorphemesFromFact(self, fact, withLemme = False):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (fact.id,)
        sql =  "Select m.id, m.status, m.status_changed, m.morph_lemme_id, m.score "
        if withLemme:
            sql += ", ml.base, ml.pos, ml.sub_pos, ml.read, ml.id "
        sql += "From Morphemes m, FactsMorphemes mf "
        if withLemme:
            sql += ", MorphemeLemmes ml "
        sql += "Where mf.morpheme_id = m.id and mf.fact_id = ?"
        if withLemme:
            sql += " and ml.id == m.morph_lemme_id "
        
        c.execute(sql, t)
        
        morphemes = []
        for row in c:
            morphLemme = None
            if withLemme:
                morphLemme = MorphemeLemme(row[5], None, row[6], row[7], row[8], row[9])
            morphemes.append(Morpheme(row[1], row[2], row[3], morphLemme, row[4], row[0]))
            
        c.close()
        
        return morphemes
    
    def clearMorphemesStatus(self): #FIXME: language
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Update Morphemes Set status_changed = 0")
        
        db.commit()
        c.close()
        
    def getAllMorphemes(self): #FIXME: language
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("select mm.base, mm.read from MorphemeLemmes mm, Morphemes m where mm.id = m.morph_lemme_id and (m.status = 2 or m.status = 3)")
        result = set()
        for row in c:
            result.append((row[0], row[1]))
        
        c.close()
        
        return result
    
    def getAllKnownSimpleMorphemes(self): # FIXME: language
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("select mm.base, mm.read from MorphemeLemmes mm, Morphemes m where mm.id = m.morph_lemme_id and (m.status = 2 or m.status = 3)")
        result = set()
        for row in c:
            result.add((row[0], row[1]))
        
        c.close()
        
        return result
        
    def getAllKnownBaseMorphemes(self): # FIXME: language
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("select mm.base from MorphemeLemmes mm, Morphemes m where mm.id = m.morph_lemme_id and (m.status = 2 or m.status = 3)")
        result = set()
        for row in c:
            result.add(row[0])
        
        c.close()
        
        return result
