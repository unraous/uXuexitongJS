# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'a.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 700)
        MainWindow.setStyleSheet(u"QMainWindow {\n"
"                background-color: #2D2D30;\n"
"                }\n"
"\n"
"                QLabel {\n"
"                color: #E0E0E0;\n"
"                font-family: 'Arial', sans-serif;\n"
"                }\n"
"\n"
"                QPushButton {\n"
"                background-color: #0078D7;\n"
"                color: white;\n"
"                border: none;\n"
"                border-radius: 4px;\n"
"                padding: 8px 16px;\n"
"                font-size: 14px;\n"
"                font-weight: bold;\n"
"                }\n"
"\n"
"                QPushButton:hover {\n"
"                background-color: #1E88E5;\n"
"                }\n"
"\n"
"                QPushButton:pressed {\n"
"                background-color: #0060AC;\n"
"                }\n"
"\n"
"                QWidget#gameContainer1, QWidget#gameContainer2 {\n"
"                background-color: #1E1E1E;\n"
"                border: 2px solid #3E3E40;\n"
"                border-radius: 5px;\n"
"                }\n"
"")
        self.actionNew_Game = QAction(MainWindow)
        self.actionNew_Game.setObjectName(u"actionNew_Game")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionControls = QAction(MainWindow)
        self.actionControls.setObjectName(u"actionControls")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mainLayout = QGridLayout(self.centralwidget)
        self.mainLayout.setObjectName(u"mainLayout")
        self.titleLabel = QLabel(self.centralwidget)
        self.titleLabel.setObjectName(u"titleLabel")
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setStyleSheet(u"color: #29B6F6;")
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.titleLabel, 0, 0, 1, 4)

        self.playerVsPlayerButton = QPushButton(self.centralwidget)
        self.playerVsPlayerButton.setObjectName(u"playerVsPlayerButton")
        self.playerVsPlayerButton.setMinimumSize(QSize(0, 40))
        icon = QIcon()
        icon.addFile(u"icons/users.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.playerVsPlayerButton.setIcon(icon)

        self.mainLayout.addWidget(self.playerVsPlayerButton, 1, 0, 1, 2)

        self.playerVsAiButton = QPushButton(self.centralwidget)
        self.playerVsAiButton.setObjectName(u"playerVsAiButton")
        self.playerVsAiButton.setMinimumSize(QSize(0, 40))
        icon1 = QIcon()
        icon1.addFile(u"icons/robot.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.playerVsAiButton.setIcon(icon1)

        self.mainLayout.addWidget(self.playerVsAiButton, 1, 2, 1, 2)

        self.gameContainer1 = QWidget(self.centralwidget)
        self.gameContainer1.setObjectName(u"gameContainer1")
        self.gameContainer1.setMinimumSize(QSize(250, 450))

        self.mainLayout.addWidget(self.gameContainer1, 2, 0, 1, 2)

        self.gameContainer2 = QWidget(self.centralwidget)
        self.gameContainer2.setObjectName(u"gameContainer2")
        self.gameContainer2.setMinimumSize(QSize(250, 450))

        self.mainLayout.addWidget(self.gameContainer2, 2, 2, 1, 2)

        self.scoreLabel1 = QLabel(self.centralwidget)
        self.scoreLabel1.setObjectName(u"scoreLabel1")
        font1 = QFont()
        font1.setPointSize(16)
        font1.setBold(True)
        self.scoreLabel1.setFont(font1)
        self.scoreLabel1.setStyleSheet(u"color: #FFC107;")
        self.scoreLabel1.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.scoreLabel1, 3, 0, 1, 2)

        self.scoreLabel2 = QLabel(self.centralwidget)
        self.scoreLabel2.setObjectName(u"scoreLabel2")
        self.scoreLabel2.setFont(font1)
        self.scoreLabel2.setStyleSheet(u"color: #FFC107;")
        self.scoreLabel2.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.scoreLabel2, 3, 2, 1, 2)

        self.infoLabel = QLabel(self.centralwidget)
        self.infoLabel.setObjectName(u"infoLabel")
        font2 = QFont()
        font2.setPointSize(14)
        font2.setItalic(True)
        self.infoLabel.setFont(font2)
        self.infoLabel.setStyleSheet(u"color: #9E9E9E;")
        self.infoLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.infoLabel, 4, 0, 1, 4)

        self.controlsLabel = QLabel(self.centralwidget)
        self.controlsLabel.setObjectName(u"controlsLabel")
        font3 = QFont()
        font3.setPointSize(12)
        self.controlsLabel.setFont(font3)
        self.controlsLabel.setStyleSheet(u"color: #80CBC4;")
        self.controlsLabel.setAlignment(Qt.AlignCenter)

        self.mainLayout.addWidget(self.controlsLabel, 5, 0, 1, 4)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 24))
        self.menuGame = QMenu(self.menubar)
        self.menuGame.setObjectName(u"menuGame")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuGame.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuGame.addAction(self.actionNew_Game)
        self.menuGame.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionControls)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Tetris Battle", None))
        self.actionNew_Game.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u6e38\u620f", None))
#if QT_CONFIG(shortcut)
        self.actionNew_Game.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionControls.setText(QCoreApplication.translate("MainWindow", u"\u63a7\u5236\u8bf4\u660e", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"\u4fc4\u7f57\u65af\u65b9\u5757\u5bf9\u6218", None))
        self.playerVsPlayerButton.setText(QCoreApplication.translate("MainWindow", u"\u73a9\u5bb6\u5bf9\u6218", None))
        self.playerVsAiButton.setText(QCoreApplication.translate("MainWindow", u"\u4eba\u673a\u5bf9\u6218", None))
        self.scoreLabel1.setText(QCoreApplication.translate("MainWindow", u"\u73a9\u5bb61\u5f97\u5206: 0", None))
        self.scoreLabel2.setText(QCoreApplication.translate("MainWindow", u"\u73a9\u5bb62\u5f97\u5206: 0", None))
        self.infoLabel.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u6e38\u620f\u6a21\u5f0f\u5f00\u59cb", None))
        self.controlsLabel.setText(QCoreApplication.translate("MainWindow", u"\u73a9\u5bb61: WASD\u63a7\u5236 | \u73a9\u5bb62: \u65b9\u5411\u952e\u63a7\u5236", None))
        self.menuGame.setTitle(QCoreApplication.translate("MainWindow", u"\u6e38\u620f", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"\u5e2e\u52a9", None))
    # retranslateUi

