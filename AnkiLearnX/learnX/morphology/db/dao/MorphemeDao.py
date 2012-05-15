from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.MorphemeLemme import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *
from learnX.utils.Utils import *

import math

class MorphemeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistMorphemes(self, morphemes):
        db = self.learnXdB.openDataBase()
        
        log("select")
        
        c = db.cursor()
        morphemesToInsert = list()
        for morpheme in morphemes:
            t = (morpheme.morphLemmeId, morpheme.noteId)
            c.execute("Select id From Morphemes Where morph_lemme_id = ? and note_id = ?", t)
            row = c.fetchone()
            if row == None:
                morphemesToInsert.append(morpheme)
        c.close()
        
        log("insert")
        
        c = db.cursor()
        for morpheme in morphemesToInsert:
            t = (morpheme.noteId, morpheme.interval, morpheme.changed, morpheme.morphLemmeId)
            c.execute("Insert into Morphemes(note_id, interval, changed, morph_lemme_id) "
                      "Values (?,?,?,?)", t)
        db.commit()
        c.close()
        
        log("end")
    
        return morphemes    
    
    def updateInterval(self, cards):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        log("update interval")
        
        for card in cards:
            t = (card.interval, card.noteId)
            c.execute("Update Morphemes Set interval = ? Where note_id = ?", t)
        
        db.commit()
        c.close()
        
        log("select modified morphemes")
        
        c = db.cursor()
        noteIds = set()
        for card in cards:
            noteIds.add(card.noteId)
        noteIds = Utils.ids2str(noteIds)
        
        c.execute("Select morph_lemme_id From Morphemes where note_id in %s" % noteIds)
        morphemesModified = set()
        for row in c:
            morphemesModified.add(row[0])
        c.close()   
        
        log("mark modified notes")
        c = db.cursor()
        c.execute("Update Notes set changed = 1 "
                  "Where id in (select note_id From Morphemes where morph_lemme_id in %s group by note_id)" % Utils.ids2str(morphemesModified))
        c.close()   
        
        c = db.cursor()
        log("update morphemes")
        for lemmeId in morphemesModified:
            t = (lemmeId, lemmeId)
            c.execute("Update MorphemeLemmes set max_interval = "
                      "(select max(interval) From Morphemes where morph_lemme_id = ? group by morph_lemme_id), "
                      "changed = 1 "
                      "where id = ?", t)
        db.commit()
        c.close()
        
        log("end update interval")
        
    def updateIntervalBis(self, cards):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        log("update interval")
        
        for card in cards:
            t = (card.interval, card.noteId)
            c.execute("Update Morphemes Set interval = ? Where note_id = ?", t)
        
        db.commit()
        c.close()
        
        log("select modified morphemes")
        
        c = db.cursor()
        noteIds = set()
        for card in cards:
            noteIds.add(card.noteId)
        noteIds = Utils.ids2str(noteIds)
        
        c.execute("Select morph_lemme_id From Morphemes where note_id in %s" % noteIds)
        morphemesModified = set()
        for row in c:
            morphemesModified.add(row[0])
        c.close()   
        
        log("mark modified notes")
        c = db.cursor()
        c.execute("Update Notes set changed = 1 "
                  "Where id in (select note_id From Morphemes where morph_lemme_id in %s group by note_id)" % Utils.ids2str(morphemesModified))
        c.close()   
        
        log("create temp tables")
        
        c = db.cursor()
        c.execute("DROP TABLE IF EXISTS MorphemesMax")
        c.execute(
            "Create temporary table MorphemesMax AS select morph_lemme_id, max(interval) as max_interval "
            "From Morphemes group by morph_lemme_id")
        db.commit()
        c.close()
        
        c = db.cursor()
        log("update morphemes")
        for lemmeId in morphemesModified:
            t = (lemmeId, lemmeId)
            c.execute("Update MorphemeLemmes set max_interval = "
                      "(select max_interval From MorphemesMax where morph_lemme_id = ?), "
                      "changed = 1 "
                      "where id = ?", t)
        db.commit()
        c.close()
        
        log("end update interval")
        
