#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from learnX.morphology.service.ServicesLocator import *
from learnX.morphology.db.dto.Language import *

from learnX.interface.model.JapaneseMorphemeModel import *
from learnX.interface.model.FrenchMorphemeModel import *

class MorphemesBrowser(QDialog):
    
    def __init__(self, deck, language, allDecks, parent=None):
        super(MorphemesBrowser, self).__init__(parent)
        
        self.morphemesService = ServicesLocator.getInstance().getMorphemesService()
        self.languagesService = ServicesLocator.getInstance().getLanguagesService()
        
        if language.nameId == Language.JAPANESE:
            self.model = my_model = JapaneseMorphemeModel(deck, language, allDecks)
        elif language.nameId == Language.FRENCH:
            self.model = my_model = FrenchMorphemeModel(deck, language, allDecks)
        
        self.parent = parent
        self.resize(900, 500)
        self.setTitle()
        
        self.mainVBox = mainVBox = QVBoxLayout(self)
        
        self.filterHBox = filterHBox = QHBoxLayout(self)
        
        self.filterLabel = QLabel("Expression:")
        self.filterText = QLineEdit()
        self.filterButton = QPushButton("Search")
        self.filterButton.setFixedHeight(20)
        
        self.connect(self.filterText, SIGNAL("returnPressed()"), self.updateFilter)
        self.connect(self.filterButton, SIGNAL("clicked()"), self.updateFilter)
        
        self.customFilterLabel = QLabel("Filter:")
        self.customFilter = customFilter = QComboBox()
        
        customFilter.addItem("Show All")
        customFilter.insertSeparator(self.customFilter.count())
        customFilter.addItem("None")
        customFilter.addItem("Learnt")
        customFilter.addItem("Known")
        customFilter.addItem("Mature")
        customFilter.insertSeparator(self.customFilter.count())
        customFilter.addItem("Changed")
        customFilter.addItem("Un-Changed")
        
        self.posList = self.languagesService.getAllPOS(language)
        
        filterPosLabelFont = QFont()
        filterPosLabelFont.setPixelSize(12)
        
        customFilter.setFont(filterPosLabelFont) 
        
        if self.posList != None and len (self.posList) > 0:
            customFilter.insertSeparator(self.customFilter.count())
        
            for pos in self.posList:
                customFilter.addItem(pos)
                
        self.subPosList = self.languagesService.getAllSubPOS(language)
        if self.subPosList != None and len (self.subPosList) > 0:
            customFilter.insertSeparator(self.customFilter.count())
        
            for subPos in self.subPosList:
                customFilter.addItem(subPos)
        
        self.connect(customFilter, SIGNAL("activated(int)"), self.tagChanged)


        self.sortLabel = QLabel("Sort by:")
        
        self.sortOrderButton = QPushButton()
        self.sortOrderButton.setMaximumSize(QSize(20, 20))
        self.sortOrderButton.setFocusPolicy(Qt.NoFocus)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(":/icons/view-sort-ascending.png"), QIcon.Normal, QIcon.Off)
        self.sortOrderButton.setIcon(icon1)
        self.sortOrderButton.setFlat(True)
        self.sortOrder = True
        self.sortColumn = 0
        
        self.connect(self.sortOrderButton, SIGNAL("clicked()"), self.reverseOrder)
        
        self.sortBox = sortBox = QComboBox()
        for column in self.model.columns:
            sortBox.addItem(column)
        self.connect(sortBox, SIGNAL("activated(int)"), self.sort)
        
        filterHBox.addWidget(self.filterLabel)
        filterHBox.addWidget(self.filterText)
        filterHBox.addWidget(self.customFilterLabel)
        filterHBox.addWidget(self.customFilter)
        filterHBox.addWidget(self.sortLabel)
        filterHBox.addWidget(self.sortOrderButton)
        filterHBox.addWidget(self.sortBox)
        filterHBox.addWidget(self.filterButton)
        mainVBox.addLayout(filterHBox)
        
        
        tableView = QTableView()
        
        
        
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(my_model);
        
        tableView.setModel(proxyModel)
        
        headerView = QHeaderView(Qt.Horizontal)
        headerView.setResizeMode(QHeaderView.Stretch)
        headerView.setClickable(True)
        
        self.connect(headerView, SIGNAL("clicked(int)"), self.sort)
        
        tableView.setHorizontalHeader(headerView)
        tableView.verticalHeader().hide()
        tableView.setSortingEnabled(True)
        tableView.setAlternatingRowColors(True)
        tableView.setTabKeyNavigation(False)
        tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.tableView = tableView
        
        mainVBox.addWidget(tableView)
        
    def setTitle(self):
        
        initMorphemesLen = str(self.model.initMorphemesLen)
        currentMorphemesLen = str(self.model.currentMorphemesLen)
        self.setWindowTitle('Browser Morphemes - ' + currentMorphemesLen + " of " + initMorphemesLen + " cards shown")
        
    def tagChanged(self, idx):
        posStartIdx = 9
        subPosStartIdx = posStartIdx
        if len(self.posList) > 0:
            subPosStartIdx += len(self.posList) + 1
        if idx == 0:
            filter = ""
        elif idx == 2:
            filter = "status:None"
        elif idx == 3:
            filter = "status:Learnt"
        elif idx == 4:
            filter = "status:Known"
        elif idx == 5:
            filter = "status:Mature"
        elif idx == 7:
            filter = "is:changed"
        elif idx == 8:
            filter = "-is:changed"
        elif idx > posStartIdx and idx <= (posStartIdx + len(self.posList)):
            log(idx)
            log(len(self.posList))
            log(posStartIdx)
            filter = "pos:" + self.posList[idx - posStartIdx - 1]
        elif idx > subPosStartIdx and idx <= (subPosStartIdx + len(self.subPosList)):
            filter = "sub_pos:" + self.subPosList[idx - subPosStartIdx - 1]
        
        self.filterText.setText(filter)
        self.updateFilter()
        
    def updateFilter(self):
        self.model.searchText = self.filterText.text()
        self.model.showMatching()
        self.setTitle()
    
    def reverseOrder(self):
        if self.sortOrder:
            self.sortOrderButton.setIcon(QIcon(":/icons/view-sort-descending.png"))
        else:
            self.sortOrderButton.setIcon(QIcon(":/icons/view-sort-ascending.png"))
        self.sortOrder = not self.sortOrder
        self.sort(self.sortColumn)
        
    def sort(self, columnId):
        self.sortColumn = columnId
        if self.sortOrder:
            self.tableView.sortByColumn(columnId, Qt.DescendingOrder)
        else:
            self.tableView.sortByColumn(columnId, Qt.AscendingOrder)
