QtInstalled = False
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    QtInstalled = True
except ImportError:
    try:
        #from PySide2.QtCore import *
        #from PySide2.QtGui import *
        #from PySide2.QtWidgets import *
        pass
    except ImportError:
        pass