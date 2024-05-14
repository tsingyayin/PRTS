from typing import *
from enum import *
import random, os
from ._Config import *
from ._AccountManager import *
from ._TempStringManager import *
from ._EmailHost import *

class PRTS:
    Config:Any = None
    AccountManager:Any = None
    TempStringManager:Any = None
    EmailHost:Any = None
    def __init__(this, configPath:str = "./PRTS.yml"):
        this.Config = PRTSConfig(configPath)
        this.EmailHost = PRTSEmailHost()
        this.TempStringManager = PRTSTempStringManager()
        this.AccountManager = PRTSAccountMetaManager(this.TempStringManager, this.EmailHost)
        

    
