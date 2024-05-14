from ._QtGeneral import *
from .. import *
class _PRTSGUI_AccountRegister(QWidget):
    def __init__(this, parent:QWidget = None):
        super().__init__(parent)
        this.UserNameLabel = QLabel("Username:", this)
        this.UserNameEdit = QLineEdit(this)
        this.PasswordLabel = QLabel("Password:", this)
        this.PasswordEdit = QLineEdit(this)
        this.NickNameLabel = QLabel("Nickname:", this)
        this.NickNameEdit = QLineEdit(this)
        this.EmailLabel = QLabel("E-Mail:", this)
        this.EmailEdit = QLineEdit(this)
        this.DataJsonLabel = QLabel("DataJson", this)
        this.DataJsonEdit = QTextEdit(this)
        this.RegisterButton = QPushButton("Register", this)
        this.ClearButton = QPushButton("Clear", this)
        this.Layout = QGridLayout(this)
        this.Layout.addWidget(this.ClearButton, 0, 0)
        this.Layout.addWidget(this.RegisterButton, 0, 1)
        this.Layout.addWidget(this.UserNameLabel, 1, 0)
        this.Layout.addWidget(this.UserNameEdit, 1, 1)
        this.Layout.addWidget(this.PasswordLabel, 2, 0)
        this.Layout.addWidget(this.PasswordEdit, 2, 1)
        this.Layout.addWidget(this.NickNameLabel, 3, 0)
        this.Layout.addWidget(this.NickNameEdit, 3, 1)
        this.Layout.addWidget(this.EmailLabel, 4, 0)
        this.Layout.addWidget(this.EmailEdit, 4, 1)
        this.Layout.addWidget(this.DataJsonLabel, 5, 0, 1, 2)
        this.Layout.addWidget(this.DataJsonEdit, 6, 0, 1, 2)

        this.ClearButton.clicked.connect(this.clear)

        this.clear()

    def clear(this):
        this.UserNameEdit.clear()
        this.PasswordEdit.clear()
        this.NickNameEdit.clear()
        this.EmailEdit.clear()
        this.DataJsonEdit.setText(PRTSConfig.Instance["AccountManager"]["TemplateMetaJson"])
        
class _PRTSGUI_Email(QWidget):
    def __init__(this, parent:QWidget = None):
        super().__init__(parent)
        this.SubTitleLabel = QLabel("SubTitle:", this)
        this.SubTitleEdit = QLineEdit(this)
        this.ToAddressLabel = QLabel("To Address:", this)
        this.ToAddressEdit = QLineEdit(this)
        this.ContentLabel = QLabel("Content:", this)
        this.ContentEdit = QTextEdit(this)
        this.SendButton = QPushButton("Send", this)
        this.ClearButton = QPushButton("Clear", this)
        this.Layout = QGridLayout(this)
        this.Layout.addWidget(this.ClearButton, 0, 0)
        this.Layout.addWidget(this.SendButton, 0, 1)
        this.Layout.addWidget(this.SubTitleLabel, 1, 0)
        this.Layout.addWidget(this.SubTitleEdit, 1, 1)
        this.Layout.addWidget(this.ToAddressLabel, 2, 0)
        this.Layout.addWidget(this.ToAddressEdit, 2, 1)
        this.Layout.addWidget(this.ContentLabel, 3, 0, 1, 2)
        this.Layout.addWidget(this.ContentEdit, 4, 0, 1, 2)

        this.ClearButton.clicked.connect(this.clear)

        this.clear()

    def clear(this):
        this.SubTitleEdit.clear()
        this.ToAddressEdit.clear()
        this.ContentEdit.clear()

class PRTSGUI(QWidget):
    def __init__(this, parent:QWidget = None):
        super().__init__(parent)
        this.setWindowTitle("Permission-Role-Token System | PRTS")
        this.AccountRegister = _PRTSGUI_AccountRegister(this)
        this.Email = _PRTSGUI_Email(this)
        this.Layout = QGridLayout(this)
        this.Layout.addWidget(this.AccountRegister, 0, 0, 1, 1)
        this.Layout.addWidget(this.Email, 1, 0, 1, 1)