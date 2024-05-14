# Notice: PRTS.GUI can only be used when PySide2/6 is import-able.
from typing import *
from ._QtGeneral import *
if QtInstalled:
    from ._PRTSGUI import *
else:
    class PRTSGUI:
        def __init__(this, parent:Any = None):
            print("PySide2/6 is not installed, PRTS.GUI cannot be used.")
            print("Could you please install PySide2/6 and try again?")
