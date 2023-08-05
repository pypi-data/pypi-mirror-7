#
# FBrowser.py -- File Browser plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c)  Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import os, glob
import stat, time

from ginga.misc import Bunch
from ginga import GingaPlugin

from ginga.qtw.QtHelp import QtGui, QtCore, QImage, QPixmap, QIcon
from ginga.qtw import QtHelp
from ginga import AstroImage


class FBrowser(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(FBrowser, self).__init__(fv, fitsimage)

        self.keywords = ['OBJECT', 'UT']
        self.columns = [('Name', 'name'),
                        ('Size', 'st_size'),
                        ('Mode', 'st_mode'),
                        ('Last Changed', 'st_mtime')
                        ]
        
        self.jumpinfo = []
        homedir = os.environ['HOME']
        self.curpath = os.path.join(homedir, '*')
        self.do_scanfits = False
        self.moving_cursor = False

        # Make icons
        icondir = self.fv.iconpath
        foldericon = os.path.join(icondir, 'folder.png')
        image = QImage(foldericon)
        pixmap = QPixmap.fromImage(image)
        self.folderpb = QIcon(pixmap)
        fileicon = os.path.join(icondir, 'file.png')
        image = QImage(fileicon)
        pixmap = QPixmap.fromImage(image)
        self.filepb = QIcon(pixmap)
        fitsicon = os.path.join(icondir, 'fits.png')
        image = QImage(fitsicon)
        pixmap = QPixmap.fromImage(image)
        
        self.fitspb = QIcon(pixmap)


    def build_gui(self, container):

        widget = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout()
        vbox.setContentsMargins(2, 2, 2, 2)
        widget.setLayout(vbox)

        # create the table
        #table = QtGui.QTableWidget()
        #table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #table.setDragEnabled(True)
        table = DragTable(plugin=self)
        table.setShowGrid(False)
        table.verticalHeader().hide()
        table.setColumnCount(len(self.columns))
        col = 0
        for hdr, kwd in self.columns:
            item = QtGui.QTableWidgetItem(hdr)
            table.setHorizontalHeaderItem(col, item)
            col += 1

        vbox.addWidget(table, stretch=1)
        table.itemDoubleClicked.connect(self.itemclicked_cb)
        self.treeview = table
        
        self.entry = QtGui.QLineEdit()
        vbox.addWidget(self.entry, stretch=0, alignment=QtCore.Qt.AlignTop)
        self.entry.returnPressed.connect(self.browse_cb)

        hbox = QtHelp.HBox()
        btn = QtGui.QPushButton("Load")
        btn.clicked.connect(lambda w: self.load_cb())
        hbox.addWidget(btn, stretch=0)
        btn = QtGui.QPushButton("Save Image As")
        hbox.addWidget(btn, stretch=0)
        self.entry2 = QtGui.QLineEdit()
        hbox.addWidget(self.entry2, stretch=1)
        vbox.addWidget(hbox, stretch=0, alignment=QtCore.Qt.AlignTop)
        self.entry2.returnPressed.connect(self.save_as_cb)
        btn.clicked.connect(lambda w: self.save_as_cb())

        btns = QtHelp.HBox()
        layout = btns.layout()
        layout.setSpacing(3)

        btn = QtGui.QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)
        btn = QtGui.QPushButton("Refresh")
        btn.clicked.connect(self.refresh)
        layout.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)
        btn = QtGui.QPushButton("Make Thumbs")
        btn.clicked.connect(self.make_thumbs)
        layout.addWidget(btn, stretch=0, alignment=QtCore.Qt.AlignLeft)

        vbox.addWidget(btns, stretch=0, alignment=QtCore.Qt.AlignLeft)

        cw = container.get_widget()
        cw.addWidget(widget, stretch=1)

    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_local_plugin(chname, str(self))
        return True

    def file_icon(self, bnch):
        if bnch.type == 'dir':
            pb = self.folderpb
        elif bnch.type == 'fits':
            pb = self.fitspb
        else:
            pb = self.filepb
        return pb

    def open_file(self, path):
        self.logger.debug("path: %s" % (path))

        if path == '..':
            curdir, curglob = os.path.split(self.curpath)
            path = os.path.join(curdir, path, curglob)
            
        if os.path.isdir(path):
            path = os.path.join(path, '*')
            self.browse(path)

        elif os.path.exists(path):
            #self.fv.load_file(path)
            uri = "file://%s" % (path)
            self.fitsimage.make_callback('drag-drop', [uri])

        else:
            self.browse(path)

    def load_cb(self):
        curdir, curglob = os.path.split(self.curpath)
        sm = self.treeview.selectionModel()
        paths = [ os.path.join(curdir,
                               self.treeview.model().data(row, 0))
                  for row in sm.selectedRows() ]
        #self.fv.dragdrop(self.fitsimage, paths)
        self.fv.gui_do(self.fitsimage.make_callback, 'drag-drop',
                       paths)
        
    def get_info(self, path):
        dirname, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        ftype = 'file'
        if os.path.isdir(path):
            ftype = 'dir'
        elif os.path.islink(path):
            ftype = 'link'
        elif ext.lower() == '.fits':
            ftype = 'fits'

        filestat = os.stat(path)
        bnch = Bunch.Bunch(path=path, name=filename, type=ftype,
                           st_mode=filestat.st_mode, st_size=filestat.st_size,
                           st_mtime=filestat.st_mtime)
        return bnch
        
    def browse(self, path):
        self.logger.debug("path: %s" % (path))
        if os.path.isdir(path):
            dirname = path
            globname = None
        else:
            dirname, globname = os.path.split(path)
        dirname = os.path.abspath(dirname)
        if not globname:
            globname = '*'
        path = os.path.join(dirname, globname)

        # Make a directory listing
        self.logger.debug("globbing path: %s" % (path))
        filelist = list(glob.glob(path))
        filelist.sort(key=str.lower)
        filelist.insert(0, os.path.join(dirname, '..'))

        self.jumpinfo = map(self.get_info, filelist)
        self.curpath = path
        self.entry.setText(path)

        if self.do_scanfits:
            self.scan_fits()
            
        self.makelisting()

    def makelisting(self):
        table = self.treeview
        table.clearContents()
        row = 0
        table.setRowCount(len(self.jumpinfo))

        table.setSortingEnabled(True)
        for bnch in self.jumpinfo:
            item1 = QtGui.QTableWidgetItem(bnch.name)
            icon = self.file_icon(bnch)
            item1.setIcon(icon)
            item1.setFlags(item1.flags() & ~QtCore.Qt.ItemIsEditable)
            item2 = QtGui.QTableWidgetItem(str(bnch.st_size))
            item2.setFlags(item2.flags() & ~QtCore.Qt.ItemIsEditable)
            item3 = QtGui.QTableWidgetItem(oct(bnch.st_mode))
            item3.setFlags(item2.flags() & ~QtCore.Qt.ItemIsEditable)
            item4 = QtGui.QTableWidgetItem(time.ctime(bnch.st_mtime))
            item4.setFlags(item2.flags() & ~QtCore.Qt.ItemIsEditable)
            table.setItem(row, 0, item1)
            table.setItem(row, 1, item2)
            table.setItem(row, 2, item3)
            table.setItem(row, 3, item4)
            row += 1
        #table.setSortingEnabled(True)
        table.resizeColumnsToContents()
            
    def scan_fits(self):
        for bnch in self.jumpinfo:
            if not bnch.type == 'fits':
                continue
            if not bnch.has_key('kwds'):
                try:
                    in_f = AstroImage.pyfits.open(bnch.path, 'readonly')
                    try:
                        kwds = {}
                        for kwd in self.keywords:
                            kwds[kwd] = in_f[0].header.get(kwd, 'N/A')
                        bnch.kwds = kwds
                    finally:
                        in_f.close()
                except Exception, e:
                    continue

    def refresh(self):
        self.browse(self.curpath)
        
    def scan_headers(self):
        self.browse(self.curpath)
        
    def browse_cb(self):
        path = str(self.entry.text()).strip()
        self.browse(path)
        
    def save_as_cb(self):
        path = str(self.entry2.text()).strip()
        if not path.startswith('/'):
            path = os.path.join(self.curpath, path)

        image = self.fitsimage.get_image()
        self.fv.error_wrap(image.save_as_file, path)
        
    def get_path_at_row(self, row):
        item2 = self.treeview.item(row, 0)
        name = str(item2.text())
        if name != '..':
            curdir, curglob = os.path.split(self.curpath)
            path = os.path.join(curdir, name)
        else:
            path = name
        return path

    def itemclicked_cb(self, item):
        path = self.get_path_at_row(item.row())
        self.open_file(path)
        
    def make_thumbs(self):
        path = self.curpath
        self.logger.info("Generating thumbnails for '%s'..." % (
            path))
        filelist = glob.glob(path)
        filelist.sort(key=str.lower)

        # find out our channel
        chname = self.fv.get_channelName(self.fitsimage)
        
        # Invoke the method in this channel's Thumbs plugin
        # TODO: don't expose gpmon!
        rsobj = self.fv.gpmon.getPlugin('Thumbs')
        self.fv.nongui_do(rsobj.make_thumbs, chname, filelist)

    def start(self):
        self.win = None
        self.browse(self.curpath)

    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def stop(self):
        pass
        
    def redo(self):
        return True
    
    def __str__(self):
        return 'fbrowser'


class DragTable(QtGui.QTableWidget):
    # This class exists only to let us drag and drop files from the
    # file pane into the Ginga widget.
    
    def __init__(self, parent=None, plugin=None):
        super(DragTable, self).__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.plugin = plugin

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, event):
        indices = self.selectedIndexes()
        selected = set()
        for index in indices:
            selected.add(index.row())

        urls = []
        for row in selected:
            path = "file://" + self.plugin.get_path_at_row(row)
            url = QtCore.QUrl(path)
            urls.append(url)

        mimeData = QtCore.QMimeData()
        mimeData.setUrls(urls)
        drag = QtHelp.QDrag(self)
        drag.setMimeData(mimeData)
        ## pixmap = QPixmap(":/drag.png")
        ## drag.setHotSpot(QPoint(pixmap.width()/3, pixmap.height()/3))
        ## drag.setPixmap(pixmap)
        if QtHelp.have_pyqt5:
            result = drag.exec_(QtCore.Qt.MoveAction)
        else:
            result = drag.start(QtCore.Qt.MoveAction)

    def mouseMoveEvent(self, event):
        self.startDrag(event)
        
#END
