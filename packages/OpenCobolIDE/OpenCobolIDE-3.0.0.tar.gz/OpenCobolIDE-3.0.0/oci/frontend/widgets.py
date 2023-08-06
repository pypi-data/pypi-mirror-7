"""
Widgets in this module are used as promoted widgets in QtDesigner
"""
from pyqode.core.qt import QtCore, QtGui, QtWidgets


class RecentFilesListWidget(QtWidgets.QListWidget):
    """
    A custom list widget which keeps track of the mouse button that is
    pressed. It also changes the mouse cursor to a pointing hand cursor
    when the mouse cursor is over a list item.

    This class is used in QHomeWidget to ignore itemClicked when the right
    button is pressed.
    """
    remove_current_requested = QtCore.Signal()
    clear_requested = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pt):
        actionRemove = QtWidgets.QAction("Remove from recent files list", self)
        actionClear = QtWidgets.QAction('Clear recent files list', self)
        actionRemove.triggered.connect(self.remove_current_requested)
        actionClear.triggered.connect(self.clear_requested)
        actionClear.setIcon(QtGui.QIcon.fromTheme(
            'edit-clear', QtGui.QIcon(':/ide-icons/rc/edit-clear.png')))
        menu = QtWidgets.QMenu()
        menu.addAction(actionRemove)
        menu.addAction(actionClear)
        menu.exec_(self.mapToGlobal(pt))

    def mousePressEvent(self, e):
        """
        Keeps track of the pressed button
        """
        self.mouseButton = e.button()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        """
        Display a pointing hand cursor when over an item. The cursor is
        reset to an ArrowCursor if there are no item under the cursor.
        """
        item = self.itemAt(e.pos())
        super().mouseMoveEvent(e)
        self.setCursor(QtCore.Qt.PointingHandCursor if item else
            QtCore.Qt.ArrowCursor)
        if item:
            self.setCurrentRow(self.row(item))
