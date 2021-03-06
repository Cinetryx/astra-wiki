# https://stackoverflow.com/questions/16879971/example-of-the-right-way-to-use-qthread-in-pyqt
from .Common import *
from .Device import *
from .QtDeviceSelection import *
from .QtDeviceViewer import *
from .QtCV import *
from .QtPointCloud import *


class DepthInterface(QtGui.QMainWindow):

    def __init__(self, args):
        self.parent_ = args.pop('parent', None)
        self.args = args
        super(QtGui.QMainWindow, self).__init__(self.parent_)
        self.show_gl = args['3d']
        self.debugging = args['debug']
        if self.debugging:
            logger.info("Enabling Debug Mode")
            logger.root.setLevel(logging.DEBUG)
        self.windowTitle = args.pop('window_title', "Depth Interface")
        self.setWindowTitle(self.windowTitle)
        self._set_window_size(1024,600,False)

        self.__layout()
        self.__init_menu()
        self.statusBar().showMessage('Listing Devices')
        self.show_device_list()
        self.statusBar().showMessage('Ready')

        if args.pop('open_any'):
            self.device_list.open_any()

    def __layout(self):
        _widget = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(_widget)

        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setTabPosition(1)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self._closeTab)

        self.layout.addWidget(self.tabWidget)
        self.setCentralWidget(_widget)

    def __init_menu(self):
        self.mainMenu = self.menuBar()
        self.mainMenu.setNativeMenuBar(False)
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.viewMenu = self.mainMenu.addMenu('View')
        self.toolsMenu = self.mainMenu.addMenu('Tools')
        #self.dataMenu = self.mainMenu.addMenu('Data')
        self.helpMenu = self.mainMenu.addMenu('Help')
        if self.debugging:
            self.debugMenu = self.mainMenu.addMenu('Debug')

        '''
        https://stackoverflow.com/questions/10368947/how-to-make-qmenu-item-checkable-pyqt4-python#10369171
        https://stackoverflow.com/a/20931230
        FILE            VIEW           TOOLS         HELP        DEBUG
        ---------------------------------------------------------------
        Open            
          > ONI
          > Device
        Close
        --
        Exit
        '''

        exitButton = QtGui.QAction(QtGui.QIcon(), 'Exit', self)
        exitButton.setShortcut("Ctrl+Q")
        exitButton.setStatusTip("Exit Application")
        exitButton.triggered.connect(self._close_dialog)
        self.fileMenu.addAction(exitButton)


    def _close_dialog(self, *args):
        if QtGui.QMessageBox.question(None, self.windowTitle, "Are you sure you want to quit?",
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.close()
    
    def _destruct(self, *args):
        logging.debug("Destructing")
        self.close()
        openni2.unload()
        QtGui.QApplication.quit()

    def _set_window_size(self, width=800, height=600, resizable=False):
        self.resize(width, height)
        if not resizable:
            self.setMinimumSize(width, height)
            self.setMaximumSize(width, height)

    def _closeTab (self, currentIndex):
        currentQWidget = self.tabWidget.widget(currentIndex)
        currentQWidget._destroy()
        currentQWidget.deleteLater()
        self.tabWidget.removeTab(currentIndex)   

    def add_tab(self, cls, tooltip=None, closable=False, icon=None):
        name = "Unknown"
        if hasattr(cls, "objectName"):
            name = cls.objectName()
        tab = self.tabWidget.addTab(cls, name)
        if tooltip:
            self.tabWidget.setTabToolTip(tab, str(tooltip, 'ascii'))
        if not closable:
            self.tabWidget.tabBar().setTabButton(tab, QtGui.QTabBar.RightSide,None)
        if icon:
            self.tabWidget.setTabIcon(icon)
        self.tabWidget.setCurrentIndex(tab)

    def show_device_list(self):
        self.device_list = DeviceSelection(self)
        self.add_tab(self.device_list)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = DepthInterface()
    main.show()
    app.aboutToQuit.connect(main._destruct)
    app.exec_()
