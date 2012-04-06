from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Fact import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *

class FactDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
        
    def insert(self, fact):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        if fact.deck:
            fact.deckId = fact.deck.id
        
        t = (fact.deckId, fact.ankiFactId, fact.lastUpdated, fact.expressionHash, fact.morphemesChanged, fact.status, fact.statusChanged, fact.score)
        c.execute("Insert into Facts(deck_id, anki_fact_id, last_updated, expression_hash, morphemes_changed, status, status_changed, score)"
                  "Values (?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        
        t = (fact.deckId, fact.ankiFactId)
        c.execute("Select id From Facts Where deck_id = ? and anki_fact_id = ?", t)
        
        for row in c:
            fact.id = row[0]
        
        c.close()
    
        return fact
    
    def insertAll(self, facts):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for fact in facts:
            if fact.deck:
                fact.deckId = fact.deck.id
            
            t = (fact.deckId, fact.ankiFactId, fact.lastUpdated, fact.expressionHash, fact.morphemesChanged, fact.status, fact.statusChanged, fact.score)
            c.execute("Insert into Facts(deck_id, anki_fact_id, last_updated, expression_hash, morphemes_changed, status, status_changed, score)"
                      "Values (?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        
        for fact in facts:
            t = (fact.deckId, fact.ankiFactId)
            c.execute("Select id From Facts Where deck_id = ? and anki_fact_id = ?", t)
            
            for row in c:
                fact.id = row[0]
        
        c.close()
    
    def update(self, fact):
        
        db = self.learnXdB.openDataBase()    
        c = db.cursor()
        
        t = (fact.deckId, fact.ankiFactId, fact.lastUpdated, fact.expressionHash, fact.morphemesChanged, fact.status,
             fact.statusChanged, fact.score, fact.id)
        c.execute("Update Facts Set Where deck_id = ?, anki_fact_id = ?, last_updated = ?, "
                  "expression_hash = ?, morphemes_changed = ?, status = ?, status_changed = ?, score = ?"
                  "Where id = ?", t)
        db.commit()
        c.close()
        
        return fact
    
    def updateAll(self, facts):
        db = self.learnXdB.openDataBase()    
        c = db.cursor()
        
        for fact in facts:
            t = (fact.deckId, fact.ankiFactId, fact.lastUpdated, fact.expressionHash, fact.morphemesChanged, fact.status,
                 fact.statusChanged, fact.score, fact.id)
            c.execute("Update Facts Set deck_id = ?, anki_fact_id = ?, last_updated = ?, "
                      "expression_hash = ?, morphemes_changed = ?, status = ?, status_changed = ?, score = ? "
                      "Where id = ?", t)
        db.commit()
        c.close()
        
        return facts
    
    def findByAnkiFactId(self, deck, ankiFactId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        t = (deck.id, ankiFactId)
        c.execute("Select * From Facts Where deck_id = ? and anki_fact_id = ?", t)
        
        fact = None
        for row in c:
            fact = Fact(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0])
            fact.deck = deck

        c.close()
        
        return fact
    
    def findById(self, factId):
    
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        t = (factId,)
        c.execute("Select * From Facts Where id = ?", t)
        
        fact = None
        for row in c:
            fact = Fact(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0])

        c.close()
        
        return fact
    
    
    def findByChangedMorphemes(self, decksId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        sql = "Select distinct f.id, f.deck_id, f.anki_fact_id, f.last_updated, f.expression_hash, "
        sql += "f.morphemes_changed, f.status, f.status_changed, f.score "
        sql += "From Morphemes m, FactsMorphemes mf, Facts f "
        sql += "Where mf.morpheme_id = m.id and f.id = mf.fact_id and m.status_changed = 1 "
        
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
        
        facts = []
        for row in c:
            facts.append(Fact(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]))
        
        c.close()
        
        return facts
    
    def selectAllChanged(self, decksId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        sql = "Select * From Facts Where status_changed = 1 "
        
        t = []
        if decksId != None and len(decksId) > 0:
            sql += "and ("
            i = 1
            for deckId in decksId:
                t.append(deckId)
                sql += "deck_id = ?"
                if i < len(decksId):
                    sql += " or "
                i += 1
            sql += ")"
        
        if len(t) > 0:
            c.execute(sql, t)
        else:
            c.execute(sql)
        
        facts = []
        for row in c:
            facts.append(Fact(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]))
        
        c.close()
        
        return facts
        
    
    def insertFactMorphemes(self, fact, morphemes):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        t = (fact.id,)
        c.execute("Delete From FactsMorphemes Where fact_id = ?", t)
        
        db.commit()
        c.close()
        
        c = db.cursor()
        for morpheme in morphemes:
            t = (fact.id, morpheme.id)
            c.execute("Insert Into FactsMorphemes(fact_id, morpheme_id) Values(?,?)", t)
        db.commit()
        c.close()
        
    def insertAllFactMorphemes(self, facts):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        for fact in facts:
            t = (fact.id,)
            c.execute("Delete From FactsMorphemes Where fact_id = ?", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        for fact in facts:
            for morpheme in fact.morphemes:
                t = (fact.id, morpheme.id)
                c.execute("Insert Into FactsMorphemes(fact_id, morpheme_id) Values(?,?)", t)
        db.commit()
        c.close()
    
    def clearAllFactsStatus(self, decksId):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "Update Facts Set status_changed = 0 "

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
        