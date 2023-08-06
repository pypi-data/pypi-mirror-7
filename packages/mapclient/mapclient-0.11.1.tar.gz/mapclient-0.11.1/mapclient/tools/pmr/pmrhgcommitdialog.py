'''
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland
    
This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
'''
from PySide import QtGui

from mapclient.tools.pmr.ui_pmrhgcommitdialog import Ui_PMRHgCommitDialog

class PMRHgCommitDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self._ui = Ui_PMRHgCommitDialog()
        self._ui.setupUi(self)

        self._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText('Commit')
        self._ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self._handleCommit)

    def _handleCommit(self):
        if len(self._ui.commentTextEdit.toPlainText()):
            self.accept()
        else:
            QtGui.QMessageBox.warning(
                self, 'Error', 'Missing comment')

    def username(self):
        return self._ui.usernameLineEdit.text()
    
    def password(self):
        return self._ui.passwordLineEdit.text()
    
    def comment(self):
        return self._ui.commentTextEdit.toPlainText()
    
