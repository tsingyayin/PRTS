if __name__ == "__main__":
    import sys
    from PRTS import *
    from PRTS.GUI import *
    app = QApplication(sys.argv)
    time.sleep(5)
    PRTS()
    sguard = PRTSServerGuardian()
    PRTS.Instance.ScheduleManager.addSchedule(sguard)
    gui = PRTSGUI()
    gui.show()
    sys.exit(app.exec())