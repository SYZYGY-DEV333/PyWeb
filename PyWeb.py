#!/usr/bin/env python3
# PyWeb v1.0
# SYZYGY-DEV333
# Light, Fast web browser in Python and PyQt
# Apache Version 2

# edit search engine on line 275
# edit home page on line 383
import sys
import json
try:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtNetwork import *
    from PyQt5.QtWebKit import *
    from PyQt5.QtWebKitWidgets import *
except:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4.QtNetwork import *
    from PyQt4.QtWebKit import *

starturl = "http://www.google.com/"

def shortTitle(title=""):
    return title[:24] + '...' if len(title) > 24 else title

hosts = []
try: f = open("hosts", "r")
except: pass
else:
    try: hosts = [line for line in [line.split(" ")[1].replace("\n", "") for line in f.readlines() if len(line.split(" ")) > 1 and not line.startswith("#") and len(line) > 1] if line != ""]
    except: pass
    f.close()

class NetworkAccessManager(QNetworkAccessManager):
    def __init__(self, *args, **kwargs):
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
        self.authenticationRequired.connect(self.provideAuthentication)
    def provideAuthentication(self, reply, auth):
        username = QInputDialog.getText(None, "Authentication", "Enter your username:", QLineEdit.Normal)
        if username[1]:
            auth.setUser(username[0])
            password = QInputDialog.getText(None, "Authentication", "Enter your password:", QLineEdit.Password)
            if password[1]:
                auth.setPassword(password[0])
    def createRequest(self, op, request, device=None):
        url = request.url()
        block = url.authority() in hosts
        if block:
            return QNetworkAccessManager.createRequest(self, self.GetOperation, QNetworkRequest(QUrl("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QgdBBMTEi/JQgAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAAMSURBVAjXY/j//z8ABf4C/tzMWecAAAAASUVORK5CYII=")))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)

class BookmarksView(QMainWindow):
    bookmarksUpdated = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(BookmarksView, self).__init__(*args, **kwargs)
        self.setWindowTitle("Bookmarks")
        
        self._plainText = ""
                
        self.textEdit = QTextEdit(self)
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setFontFamily("monospace")
        self.setCentralWidget(self.textEdit)
        
        self.loadBookmarks()
        
        self.saveTimer = QTimer(self)
        self.saveTimer.timeout.connect(self.saveBookmarks)
        self.saveTimer.start(500)

    def loadBookmarks(self):
        try: f = open("bookmarks.txt", "r")
        except: return
        else:
            self.textEdit.clear()
            self.textEdit.setPlainText(f.read())
            f.close()
    
    def saveBookmarks(self):
        if self._plainText != self.textEdit.toPlainText():
            self._plainText = self.textEdit.toPlainText()
            f = open("bookmarks.txt", "w")
            f.write(self.textEdit.toPlainText())
            f.close()
            self.bookmarksUpdated.emit()

cookieJar = QNetworkCookieJar(QApplication.instance())
networkAccessManager = NetworkAccessManager(QApplication.instance())
networkAccessManager.setCookieJar(cookieJar)

incognitoCookieJar = QNetworkCookieJar(QApplication.instance())
incognitoNetworkAccessManager = NetworkAccessManager(QApplication.instance())
incognitoNetworkAccessManager.setCookieJar(incognitoCookieJar)

def loadCookies():
    global cookieJar
    try: f = open("cookies.json", "r")
    except: return
    try: rawCookies = json.load(f)
    except:
        f.close()
        return
    f.close()
    if type(rawCookies) is list:
        cookies = [QNetworkCookie().parseCookies(QByteArray(cookie))[0] for cookie in rawCookies]
        cookieJar.setAllCookies(cookies)

def saveCookies():
    global cookieJar
    f = open("cookies.json", "w")
    try: f.write(json.dumps([cookie.toRawForm().data().decode("utf-8") for cookie in cookieJar.allCookies()]))
    except: pass
    f.close()

def clearCookies():
    global cookieJar
    cookieJar.setAllCookies([])
    saveCookies()

class BookmarkAction(QAction):
    triggered2 = pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        super(BookmarkAction, self).__init__(*args, **kwargs)
        self.triggered.connect(lambda: self.triggered2.emit(self.text()))

class WebPage(QWebPage):
    def __init__(self, *args, **kwargs):
        super(WebPage, self).__init__(*args, **kwargs)
    if sys.platform.startswith("linux"):
        def userAgentForUrl(self, *args, **kwargs):
            name = QApplication.applicationName()
            return "%s %s%s %s%s" % (super(WebPage, self).userAgentForUrl(*args, **kwargs).replace(name + " ", ""), "Chrome/22.", qVersion(), name, "/:3")
    def loadHistory(self, history):
        out = QDataStream(history, QIODevice.ReadOnly)
        out.__rshift__(self.history())
    def saveHistory(self):
        byteArray = QByteArray()
        out = QDataStream(byteArray, QIODevice.WriteOnly)
        out.__lshift__(self.history())
        return byteArray

class WebView(QWebView):
    windowCreated = pyqtSignal(QWebView)
    def __init__(self, *args, incognito=False, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        self.setPage(WebPage(self))
        self.incognito = incognito
        self._findText = ""
        if not incognito:
            self.setNetworkAccessManager(networkAccessManager)
        else:
            self.setNetworkAccessManager(incognitoNetworkAccessManager)
    def setNetworkAccessManager(self, nam):
        self.page().setNetworkAccessManager(nam)
        nam.setParent(QApplication.instance())
    def createWindow(self, type):
        webview = WebView(self.parent(), incognito=self.incognito)
        self.windowCreated.emit(webview)
        return webview
        
    def find(self):
        find = QInputDialog.getText(self, "Find", "Search for:", QLineEdit.Normal, self._findText)
        if find[1]:
            self._findText = find[0]
        else:
            self._findText = ""
        self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Convenience function.
    # Find next instance of text.
    def findNext(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument)

    # Convenience function.
    # Find previous instance of text.
    def findPrevious(self):
        if not self._findText:
            self.find()
        else:
            self.findText(self._findText, QWebPage.FindWrapsAroundDocument | QWebPage.FindBackward)

    def loadHistory(self, history):
        self.page().loadHistory(history)

    def saveHistory(self):
        return self.page().saveHistory()

class ToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super(ToolBar, self).__init__(*args, **kwargs)
        self.setMovable(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

class Browser(QMainWindow):
    def __init__(self, *args, webview=None, incognito=False, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)
        self.toolBar = ToolBar(self)
        self.toolBar.setStyleSheet("QToolBar { background: transparent; border: 0; border-bottom: 1px solid palette(dark); }")
        self.addToolBar(self.toolBar)
        
        try:
            self.webView = webview
            self.webView.setParent(self)
            self.setCentralWidget(self.webView)
        except:
            self.webView = WebView(self, incognito=incognito)
            self.setCentralWidget(self.webView)
        self.webView.urlChanged.connect(self.setLocationText)
        self.webView.titleChanged.connect(self.setWindowTitle)

        self.backAction = self.webView.page().action(QWebPage.Back)
        self.backAction.setShortcut("Alt+Left")
        
        self.forwardAction = self.webView.page().action(QWebPage.Forward)
        self.forwardAction.setShortcut("Alt+Right")
        
        self.reloadAction = self.webView.page().action(QWebPage.Reload)
        self.reloadAction.setShortcuts(["Ctrl+R", "F5"])
        
        self.stopAction = self.webView.page().action(QWebPage.Stop)
        self.stopAction.setShortcut("Esc")
        
        self.toolBar.addAction(self.backAction)
        self.toolBar.addAction(self.forwardAction)
        self.toolBar.addAction(self.reloadAction)
        self.toolBar.addAction(self.stopAction)

        self.toolBar.addSeparator()

        self.findAction = QAction(self)
        self.findAction.setText("Find")
        self.findAction.setShortcut("Ctrl+F")
        self.findAction.triggered.connect(self.webView.find)
        self.findAction.setIcon(QIcon("./icons/system-search.png"))
        self.toolBar.addAction(self.findAction)

        self.findPreviousAction = QAction(self)
        self.findPreviousAction.setText("Find Next")
        self.findPreviousAction.setShortcut("Ctrl+Shift+G")
        self.findPreviousAction.triggered.connect(self.webView.findPrevious)
        self.findPreviousAction.setIcon(QIcon("./icons/media-seek-backward.png"))
        self.toolBar.addAction(self.findPreviousAction)

        self.findNextAction = QAction(self)
        self.findNextAction.setText("Find Next")
        self.findNextAction.setShortcut("Ctrl+G")
        self.findNextAction.triggered.connect(self.webView.findNext)
        self.findNextAction.setIcon(QIcon("./icons/media-seek-forward.png"))
        self.toolBar.addAction(self.findNextAction)

        self.locationBar = QLineEdit(self)
        self.locationBar.returnPressed.connect(self.loadURL)
        self.toolBar.addWidget(self.locationBar)

        self.focusLocationBarAction = QAction(self)
        self.focusLocationBarAction.setShortcuts(["Ctrl+L", "Alt+D"])
        self.focusLocationBarAction.triggered.connect(self.focusLocationBar)
        self.addAction(self.focusLocationBarAction)

    def focusLocationBar(self):
        self.locationBar.setFocus()
        self.locationBar.selectAll()

    def setLocationText(self, text):
        if type(text) is QUrl:
            text = text.toString()
        self.locationBar.setText(text)

    def loadURL(self, text=None):
        if not text:
            text = self.locationBar.text()
        if "." in text:
            self.webView.load(QUrl.fromUserInput(str(text)))
        else:
            self.webView.load(QUrl("https://www.google.com/?q=%s" % (str(text),)))

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.closedTabs = []
        
        self.menuBar = QToolBar(self)
        self.menuBar.layout().setSpacing(0)
        self.menuBar.layout().setContentsMargins(0,0,0,0)
        self.menuBar.setStyleSheet("QToolBar{background: transparent;}")
        self.menuBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menuBar.setIconSize(QSize(16,16))
        self.menuBar.setMovable(False)
        
        self.fileMenuAction = QAction(self, text="&File", shortcut="Alt+F")
        self.menuBar.addAction(self.fileMenuAction)
        self.fileMenu = QMenu(self)
        self.fileMenuAction.setMenu(self.fileMenu)
        self.fileMenuButton = self.menuBar.widgetForAction(self.fileMenuAction)
        self.fileMenuAction.triggered.connect(self.fileMenuButton.showMenu)
        
        self.bookmarksMenuAction = QAction(self, text="&Bookmarks", shortcut="Alt+B")
        self.menuBar.addAction(self.bookmarksMenuAction)
        self.bookmarksMenu = QMenu(self)
        self.bookmarksMenuAction.setMenu(self.bookmarksMenu)
        self.bookmarksMenuButton = self.menuBar.widgetForAction(self.bookmarksMenuAction)
        self.bookmarksMenuAction.triggered.connect(self.showBookmarksMenu)
        
        self.helpMenuAction = QAction(self, text="&Help", shortcut="Alt+H")
        self.menuBar.addAction(self.helpMenuAction)
        self.helpMenu = QMenu(self)
        self.helpMenuAction.setMenu(self.helpMenu)
        self.helpMenuButton = self.menuBar.widgetForAction(self.helpMenuAction)
        self.helpMenuAction.triggered.connect(self.helpMenuButton.showMenu)
        
        self.aboutAction = QAction(self)
        self.aboutAction.setText("About")
        self.aboutAction.setShortcut("F1")
        self.aboutAction.triggered.connect(self.about)
        self.helpMenu.addAction(self.aboutAction)
        self.addAction(self.aboutAction)
        
        self.bookmarkAction = QAction(self)
        self.bookmarkAction.setText("Bookmark this page")
        self.bookmarkAction.setShortcut("Ctrl+D")
        self.bookmarkAction.triggered.connect(self.addBookmark)
        
        self.bookmarks = []
        self.loadBookmarks()
        
        self.tabWidget = QTabWidget(self)
        self.tabWidget.tabBar().setShape(QTabBar.RoundedNorth)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.setCentralWidget(self.tabWidget)
        
        self.tabWidget.setCornerWidget(self.menuBar, Qt.TopLeftCorner)
        
        self.addTabAction = QAction(self)
        self.addTabAction.setText("New Tab")
        self.addTabAction.setShortcut("Ctrl+T")
        self.addTabAction.triggered.connect(self.addTab)
        self.fileMenu.addAction(self.addTabAction)
        self.addAction(self.addTabAction)

        self.addIncognitoTabAction = QAction(self)
        self.addIncognitoTabAction.setText("New Private Browsing Tab")
        self.addIncognitoTabAction.setShortcut("Ctrl+Alt+P")
        self.addIncognitoTabAction.triggered.connect(lambda: self.addTab(incognito=True))
        self.fileMenu.addAction(self.addIncognitoTabAction)
        self.addAction(self.addIncognitoTabAction)

        self.reopenTabAction = QAction(self)
        self.reopenTabAction.setText("Reopen Tab")
        self.reopenTabAction.setShortcut("Ctrl+Shift+T")
        self.reopenTabAction.triggered.connect(self.reopenTab)
        self.fileMenu.addAction(self.reopenTabAction)
        self.addAction(self.reopenTabAction)

        self.bookmarksAction = QAction(self)
        self.bookmarksAction.setText("Edit Bookmarks...")
        self.bookmarksAction.setShortcut("Ctrl+Shift+O")
        self.bookmarksAction.triggered.connect(self.viewBookmarks)
        self.addAction(self.bookmarksAction)

        self.clearCookiesAction = QAction(self)
        self.clearCookiesAction.setText("Clear cookies")
        self.clearCookiesAction.setShortcut("Ctrl+Shift+Del")
        self.clearCookiesAction.triggered.connect(clearCookies)
        self.fileMenu.addAction(self.clearCookiesAction)
        self.addAction(self.clearCookiesAction)

        self.closeTabAction = QAction(self)
        self.closeTabAction.setShortcut("Ctrl+W")
        self.closeTabAction.triggered.connect(self.closeTab)
        self.addAction(self.closeTabAction)
        
        self.titleTimer = QTimer(self)
        self.titleTimer.timeout.connect(self.updateTabTitles)
        self.titleTimer.start(500)

        if self.tabWidget.count() < 1:
            self.addTab()
            self.tabWidget.currentWidget().loadURL(starturl)

    def about(self):
        QMessageBox.about(self, "About PyWeb",
                          "<h3>%s</h3>%s" % ("Pyweb", "A simple, fast PyQt-based web browser made in Python. More information here: www.github.com/SYZYGY-DEV333/PyWeb"))

    def sizeHint(self):
        return QSize(800, 640)

    def mouseDoubleClickEvent(self, event):
        self.addTab()
    
    def showBookmarksMenu(self):
        self.bookmarksMenu.clear()
        self.bookmarksMenu.addAction(self.bookmarkAction)
        self.bookmarksMenu.addAction(self.bookmarksAction)
        self.bookmarksMenu.addSeparator()
        for bookmark in self.bookmarks:
            action = BookmarkAction(self, text=bookmark)
            action.triggered2.connect(self.loadBookmark)
            self.bookmarksMenu.addAction(action)
        self.bookmarksMenuButton.showMenu()
    
    def loadBookmark(self, url):
        try: self.tabWidget.currentWidget().webView
        except: self.addTab()
        self.tabWidget.currentWidget().webView.load(QUrl(url))
    
    def addTab(self, webview=None, incognito=False):
        tab = Browser(parent=self, webview=webview, incognito=incognito)
        self.tabWidget.addTab(tab, "(Untitled)")
        tab.webView.windowCreated.connect(self.addTab)
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)

    def viewBookmarks(self):
        for index in range(0, self.tabWidget.count()):
            if type(self.tabWidget.widget(index)) is BookmarksView:
                self.tabWidget.setCurrentIndex(index)
                return
        tab = BookmarksView(parent=self)
        self.tabWidget.addTab(tab, "Bookmarks")
        tab.bookmarksUpdated.connect(self.loadBookmarks)
        self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)

    def addBookmark(self):
        try:
            url = self.tabWidget.currentWidget().webView.url().toString()
            if not url in self.bookmarks: 
                self.bookmarks.append(url)
        except:
            pass
        self.saveBookmarks()

    def updateTabTitles(self):
        if self.tabWidget.count() < 1:
            self.setWindowTitle("PyWeb")
        else:
            for index in range(0, self.tabWidget.count()):
                title = self.tabWidget.widget(index).windowTitle()
                if len(title) < 1:
                    title = "(Untitled)"
                st = shortTitle(title)
                try:
                    if self.tabWidget.widget(index).webView.incognito:
                        st = "<<" + st + ">>"
                        title = title + " (Private Browsing)"
                except:
                    pass
                self.tabWidget.setTabText(index, st)
                if index == self.tabWidget.currentIndex():
                    self.setWindowTitle("%s - PyWeb" % (title,))

    def closeTab(self, index=None):
        if not index:
            index = self.tabWidget.currentIndex()
        widget = self.tabWidget.widget(index)
        try:
            webView = widget.webView
            history = webView.history()
            if history.canGoBack() or history.canGoForward() or webView.url().toString() not in ("", "about:blank"):
                self.closedTabs.append((webView.saveHistory(), webView.incognito))
        except:
            pass
        widget.deleteLater()

    def reopenTab(self):
        if len(self.closedTabs) > 0:
            incognito = self.closedTabs[-1][1]
            self.addTab(incognito=incognito)
            self.tabWidget.widget(self.tabWidget.count()-1).webView.loadHistory(self.closedTabs[-1][0])
            del self.closedTabs[-1]

    def loadBookmarks(self):
        try: f = open("bookmarks.txt", "r")
        except: return
        else:
            self.bookmarks = []
            bookmarks = f.readlines()
            f.close()
            for bookmark in bookmarks:
                self.bookmarks.append(bookmark.replace("\n", ""))

    def saveBookmarks(self):
        f = open("bookmarks.txt", "w")
        f.write("\n".join(self.bookmarks))
        f.close()

def main(argv):    
    app = QApplication(argv)
    app.setApplicationName("PyWeb")

    app_icon = QIcon()
    app_icon.addFile("./icons/pyweb-16.png")
    app_icon.addFile("./icons/pyweb-24.png")
    app_icon.addFile("./icons/pyweb-32.png")
    app_icon.addFile("./icons/pyweb-48.png")
    
    app.setWindowIcon(app_icon)

    loadCookies()
    
    QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
    
    win = MainWindow()
    app.aboutToQuit.connect(win.saveBookmarks)
    app.aboutToQuit.connect(saveCookies)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)
