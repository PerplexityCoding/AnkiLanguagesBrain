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
            t = (morpheme.noteId, morpheme.interval, morpheme.morphLemmeId)
            c.execute("Insert into Morphemes(note_id, interval, morph_lemme_id) "
                      "Values (?,?,?)", t)
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
        
        if len(morphemesModified) <= 0:
            return
        
        log("Compute max interval " + str(len(morphemesModified)))
        c = db.cursor()
        c.execute("Select morph_lemme_id, max(interval) From Morphemes "
                  "Where morph_lemme_id in (%s) "
                  "group by morph_lemme_id" % ",".join(str(mid) for mid in morphemesModified))
        morphesMaxes = dict()
        for row in c:
            morphesMaxes[row[0]] = row[1]
        c.close()
        
        log("Select only morphemes changed by max " + str(len(morphesMaxes)))
        c = db.cursor()
        morphemesToUpdate = list()
        
        c.execute("Select id, max_interval "
                  "From MorphemeLemmes where id in (%s)" % ",".join(str(mid) for mid, maxm in morphesMaxes.iteritems()))
        for row in c:
            if morphesMaxes[row[0]] != row[1]:
                morphemesToUpdate.append((row[0], row[1]))
        c.close()
        
        log("update morphemes changed by max " + str(len(morphemesToUpdate)))
        if len(morphemesToUpdate) > 0:
            c = db.cursor()
            for lemmeId, maxInterval in morphemesToUpdate:
                t = (maxInterval, lemmeId)
                c.execute("Update MorphemeLemmes set max_interval = ? where id = ?", t)
                s = (lemmeId,)
                c.execute("Insert Into ChangedEntities Values (?, 2)", s)
            db.commit()
            c.close()

        log("end update interval")

    def markModifiedNotes(self, morphemesModified):

        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        morphemesId = ",".join(str(m.id) for m in morphemesModified)
        c.execute("Select note_id From Morphemes where morph_lemme_id in (%s) group by note_id" % morphemesId)
        
        exNotesId = set()
        for row in c:
            exNotesId.add(row[0])
        c.close()
        
        c = db.cursor()
        for exNoteId in exNotesId:
            t = (exNoteId, )
            c.execute("Insert Into ChangedEntities Values (?, 1)", t)
        db.commit()
        c.close()

    def resetAllChanged(self):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        c.execute("Delete From ChangedEntities")
        db.commit()
        c.close()
