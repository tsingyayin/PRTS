if __name__ == "__main__":
    import sys
    from PRTS import *
    from PRTS.GUI import *
    app = QApplication(sys.argv)
    PRTS()
    gui = PRTSGUI()
    gui.show()
    sys.exit(app.exec_())