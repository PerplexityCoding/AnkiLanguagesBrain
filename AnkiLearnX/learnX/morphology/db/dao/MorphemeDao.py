from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *

class MorphemeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistAll(self, morphemes):
        db = self.learnXdB.openDataBase()
        
        morphemesToInsert = []
        c = db.cursor()
        
        for morpheme in morphemes:
            if morpheme.morph:
                morpheme.morphId = morpheme.morph.id
            t = (morpheme.morphId,)
            c.execute("Select id, status, status_changed, morph_type From Morphemes Where morph_impl_id = ?", t)
            morphemeInfo = c.fetchone()
            if morphemeInfo:
                morpheme.id = morphemeInfo[0]
                morpheme.status = morphemeInfo[1]
                morpheme.statusChanged = morphemeInfo[2]
                morpheme.type = morphemeInfo[3]
            else:
                morphemesToInsert.append(morpheme)
        c.close()
        
        c = db.cursor()
        for morpheme in morphemesToInsert:
            t = (morpheme.status, morpheme.statusChanged, morpheme.type, morpheme.morphId)
            c.execute("Insert into Morphemes(status, status_changed, morph_type, morph_impl_id) "
                      "Values (?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        for morpheme in morphemesToInsert:
            t = (morpheme.morphId,)
            c.execute("Select id From Morphemes Where morph_impl_id = ?", t)
            for row in c:
                morpheme.id = row[0]
        c.close()
    
        return morphemes    
    
    def persist(self, morpheme):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        if morpheme.morph:
            morpheme.morphId = morpheme.morph.id
        
        t = (morpheme.morphId,)
        c.execute("Select id, status, status_changed, morph_type From Morphemes Where morph_impl_id = ?", t)
        
        morphemeInfo = c.fetchone()
        if morphemeInfo:
            morpheme.id = morphemeInfo[0]
            morpheme.status = morphemeInfo[1]
            morpheme.statusChanged = morphemeInfo[2]
            morpheme.type = morphemeInfo[3]
            return morpheme
        else:
            c.close()
            
            c = db.cursor()
            t = (morpheme.status, morpheme.statusChanged, morpheme.type, morpheme.morphId)
            c.execute("Insert into Morphemes(status, status_changed, morph_type, morph_impl_id) "
                      "Values (?,?,?,?)", t)
            db.commit()
            c.close()
            
            c = db.cursor()
            
            c.execute("Select count(*) From MecabMorphemes")
            for row in c:
                morpheme.id = row[0] - 1
            c.close()
        
        return morpheme

    def updateAll(self, morphemes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        for morpheme in morphemes:
            t = (morpheme.status, morpheme.statusChanged, morpheme.type, morpheme.morphId, morpheme.id)
            c.execute("Update Morphemes Set status = ?, status_changed = ?, morph_type = ?, morph_impl_id = ? Where id = ?", t)
        
        db.commit()
        c.close()
    
        return morphemes

    def getNewStatus(self, morpheme):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "select count(c.id) from Cards c, Facts f, FactsMorphemes fm where c.fact_id = f.id and f.id = fm.fact_id and fm.morpheme_id = ? and c.status = ?"
        
        t = (morpheme.id, Card.STATUS_MATURE)
        c.execute(sql, t)
        row = c.fetchone()
        if row and row[0] > 0:
            c.close()
            return Morpheme.STATUS_MATURE
        c.close()
        
        c = db.cursor()
        t = (morpheme.id, Card.STATUS_KNOWN)
        c.execute(sql, t)
        row = c.fetchone()
        if row and row[0] > 0:
            c.close()
            return Morpheme.STATUS_KNOWN
        c.close()
        
        c = db.cursor()
        t = (morpheme.id, Card.STATUS_LEARNT)
        c.execute(sql, t)
        row = c.fetchone()
        if row and row[0] > 0:
            c.close()
            return Morpheme.STATUS_LEARNT
        c.close()
        
        return Morpheme.STATUS_NONE
        
    def getMorphemesFromCard(self, card):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (card.id,)
        c.execute("Select m.id, m.status, m.status_changed, m.morph_type, m.morph_impl_id From Morphemes m, FactsMorphemes mf, Cards c "
                  "Where mf.morpheme_id = m.id and mf.fact_id = c.fact_id and c.id = ?", t)
        morphemes = []
        for row in c:
            morphemes.append(Morpheme(row[1], row[2], row[3], row[4], None, row[0]))
            
        c.close()
        
        return morphemes
    
    def getMorphemesFromFact(self, fact):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (fact.id,)
        c.execute("Select m.id, m.status, m.status_changed, m.morph_type, m.morph_impl_id From Morphemes m, FactsMorphemes mf "
                  "Where mf.morpheme_id = m.id and mf.fact_id = ?", t)
        morphemes = []
        for row in c:
            morphemes.append(Morpheme(row[1], row[2], row[3], row[4], None, row[0]))
            
        c.close()
        
        return morphemes
    
    def clearMorphemesStatus(self):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Update Morphemes Set status_changed = 0")
        
        db.commit()
        c.close()

