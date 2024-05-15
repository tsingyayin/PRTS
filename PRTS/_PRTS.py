from typing import *
from enum import *
import random, os
from ._Config import *
from ._AccountManager import *
from ._TempStringManager import *
from ._EmailHost import *
from ._Schedule import *
class PRTS:
    Config:Any = None
    AccountManager:PRTSAccountMetaManager = None
    TempStringManager:PRTSTempStringManager = None
    EmailHost:PRTSEmailHost = None
    ScheduManager:PRTSScheduleManager = None
    Instance:'PRTS' = None
    def __init__(this, configPath:str = "./PRTS.yml"):
        if PRTS.Instance != None:
            raise Exception("PRTS is a singleton class.")
        this.Config = PRTSConfig(configPath)
        this.EmailHost = PRTSEmailHost()
        this.TempStringManager = PRTSTempStringManager()
        this.AccountManager = PRTSAccountMetaManager(this.TempStringManager)
        this.ScheduleManager = PRTSScheduleManager()
        this.AccountManager.setVerifyCodeSender(this.EmailHost)
        PRTS.Instance = this
        

    
