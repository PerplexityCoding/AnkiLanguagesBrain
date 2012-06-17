
from aqt import browser

from learnX.utils.Log import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class IntegratedMorphemesBrowser():
    def __init__(self):
        IntegratedMorphemesBrowser.oldDecksTree = browser.Browser._decksTree
        browser.Browser._decksTree = decksTree
        browser.Browser.clickMorpheme = self.clickMorpheme

    def clickMorpheme(self):
        log("clicked")
        
        self.setupTable()

    def setupTable(self):
        self.model = DataModel(self)
        self.form.tableView.setSortingEnabled(True)
        self.form.tableView.setModel(self.model)
        self.form.tableView.selectionModel()
        self.form.tableView.setItemDelegate(StatusDelegate(self, self.model))
        self.connect(self.form.tableView.selectionModel(),
                     SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                     self.onRowChanged)


def decksTree(self, root):
    
    log("buildTree Called")
    
    IntegratedMorphemesBrowser.oldDecksTree(self, root)
    
    item = self.CallbackItem("Morphemes", self.clickMorpheme)
    item.setIcon(0, QIcon(":/icons/anki-tag.png"))
    
    root.addChild(item)