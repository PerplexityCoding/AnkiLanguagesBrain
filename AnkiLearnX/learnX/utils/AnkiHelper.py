
from learnX.utils.Log import *

from aqt import mw

from anki.utils import joinFields, splitFields

class AnkiCard:
    def __init__(self, id, ivl, mod):
        self.id = id
        self.ivl = ivl
        self.mod = mod

class AnkiNote:
    def __init__(self, id, fields, mid, mod):
        self.id = id
        
        self.fields = splitFields(fields)
        self._model = mw.col.models.get(mid)
        self._fmap = mw.col.models.fieldMap(self._model)
        
        self.mod = mod
           
    # Dict interface
    ##################################################

    def keys(self):
        return self._fmap.keys()

    def values(self):
        return self.fields

    def items(self):
        return [(f['name'], self.fields[ord])
                for ord, f in sorted(self._fmap.values())]

    def _fieldOrd(self, key):
        try:
            return self._fmap[key][0]
        except:
            raise KeyError(key)

    def __getitem__(self, key):
        return self.fields[self._fieldOrd(key)]

    def __setitem__(self, key, value):
        self.fields[self._fieldOrd(key)] = value

class AnkiHelper:
    
    @staticmethod
    def getCards(did):
        
        rows = mw.col.db.all("Select c.id, c.ivl, c.mod, n.id, n.flds, n.mid, n.mod from cards c, notes n "
                             "Where c.nid = n.id and c.did = ?", did)
        ankiCards = list()
        for row in rows:
            ankiCard = AnkiCard(row[0], row[1], row[2])
            ankiCard.note = AnkiNote(row[3], row[4], row[5], row[6])
            ankiCards.append(ankiCard)

        return ankiCards

    