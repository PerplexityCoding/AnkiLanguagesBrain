from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.MorphemeLemme import *
from learnX.morphology.db.dto.Card import *
from learnX.morphology.db.dto.Note import *

from learnX.utils.Log import *
from learnX.utils.Utils import *

import math

class MorphemeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistMorphemes(self, morphemes):
        db = self.learnXdB.openDataBase()
        
        db.execute("PRAGMA journal_mode=MEMORY;")
        db.execute("PRAGMA temp_store=MEMORY;")
        db.execute("PRAGMA synchronous=OFF;")
        db.execute("PRAGMA count_changes=OFF;")
        
        log("Delete")
        c = db.cursor()
        c.execute("Delete From Morphemes where note_id in (%s)" %
                  ",".join(str(noteId) for noteId, noteMorphemes in morphemes))
        db.commit()
        c.close()
        
        log("Get all")
        c = db.cursor()
        
        allMorphemes = list()
        for noteId, noteMorphemes in morphemes:
            for morpheme in noteMorphemes:
                allMorphemes.append((morpheme.noteId, morpheme.interval, morpheme.morphLemmeId))
        
        log("Insert")
        
        c.executemany("Insert into Morphemes(note_id, interval, morph_lemme_id) Values (?,?,?)", allMorphemes)
        
        db.commit()
        
        db.execute("PRAGMA journal_mode=WAL;")
        db.execute("PRAGMA temp_store=DEFAULT;")
        db.execute("PRAGMA synchronous=ON;")
        db.execute("PRAGMA count_changes=ON;")
        
        c.close()  
    
    def updateInterval(self, cards):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        log("update interval")
        
        morphesInterval = dict()
        for card in cards:
            morphesInterval[card.noteId] = card.interval
        
        c.execute("Select note_id, interval "
                  "From Morphemes where note_id in (%s)" % ",".join(str(card.noteId) for card in cards))
        morphemesToUpdate = list()
        for row in c:
            if morphesInterval[row[0]] != row[1]:
                morphemesToUpdate.append((row[0], morphesInterval[row[0]]))
        c.close()
        
        c = db.cursor()
        for noteId, interval in morphemesToUpdate:
            t = (interval, noteId)
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
        lemmes = set()
        
        c.execute("Select id, base, pos, sub_pos, read, rank, max_interval, score "
                  "From MorphemeLemmes where id in (%s)" % ",".join(str(mid) for mid, maxm in morphesMaxes.iteritems()))
        for row in c:
            if morphesMaxes[row[0]] != row[6]:
                morphemesToUpdate.append((row[0], morphesMaxes[row[0]]))
            lemmes.add(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], morphesMaxes[row[0]], row[7], row[0]))
        c.close()
        
        log("update morphemes changed by max " + str(len(morphemesToUpdate)))
        if len(morphemesToUpdate) > 0:
            c = db.cursor()
            for lemmeId, maxInterval in morphemesToUpdate:
                t = (maxInterval, lemmeId)
                c.execute("Update MorphemeLemmes set max_interval = ? where id = ?", t)
            db.commit()
            c.close()

        log("end update interval")
        
        return lemmes

    def getModifiedNotes(self, morphemesModified):

        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        morphemesId = ",".join(str(m.id) for m in morphemesModified)
        c.execute("Select note_id From Morphemes where morph_lemme_id in (%s) group by note_id" % morphemesId)
        
        exNotesId = set()
        for row in c:
            exNotesId.add(row[0])
        c.close()

        c = db.cursor()
        c.execute("Select * From Notes where id in %s" % Utils.ids2str(exNotesId))
        
        notes = set()
        for row in c:
            notes.add(Note(row[0], row[1], row[2], row[3]))
        c.close()
        
        return notes
