from typing import *
from sqlite3 import *
import json
import datetime
from ._utils import *
from ._TempStringManager import *

class VIAccountMetaManager:
    """
    # AccountMetaManager
    ## Table - User Meta
    | username | password | nickname | email | registed_time | data |
    | -------- | -------- | -------- | ----- | ------------- | ---- |
    | Text     | Text     | Text     | Text  | Text          | Text |
    * NOTICE: This website is not working in high-performance environment, so using JSON to store user data.
    """
    DataBase: Connection
    DBCursor: Cursor
    DataBasePath: str

    def __init__(this, DataBasePath: str = "./db/account.db"):
        PRTS.AccountManager = this
        this.DataBasePath = DataBasePath
        this.DataBase = connect(DataBasePath, isolation_level=None, check_same_thread=False)
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("CREATE TABLE IF NOT EXISTS usermeta (username TEXT, password TEXT, \
nickname TEXT, email TEXT, registed_time TEXT, data TEXT)")

    def checkAccountRegistered(this, username:str)->bool:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT username FROM usermeta WHERE username=?", (username,))
        return dbCursor.fetchone() != None
    
    def checkEMailBinded(this, email:str)->bool:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT email FROM usermeta WHERE email=?", (email,))
        return dbCursor.fetchone() != None
    
    def sendVerifyCode(this, username:str, email:str)->StateCode:
        code, vcode = PRTS.TempStringManager.getVerifyCode(username)
        if code != StateCode.Success:
            return code
        PRTS.EmailHost.sendEmail(email, PRTS.EmailVerifyCodeSubTitle, 
                                    PRTS.EmailVerifyCodeTemplate.format(
                                        username=username, code=vcode,
                                        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        expire_time="5"
                                    )
                                )
        return StateCode.Success
        

    def register(this, username:str, password:str, verifyCode:str, email:str, nickname:str)->(StateCode):
        """
        Register a new account.
        username: only contains 0-9, a-z, A-Z, _, -. Length: 6-32.
        password: only contains 0-9, a-z, A-Z, _, -, !, @, #, $, %, ^, &, *, (, ), +, =, and space. Length: 6-16.
        verifyCode: only contains 0-9, a-z, A-Z. Length: 8.
        email: just same as the email that received the verify code.
        nickname: any string, even empty, but length should be less than 32.
        """
        if this.checkAccountRegistered(username):
            return StateCode.UsernameAlreadyExists
        if this.checkEMailBinded(email):
            return StateCode.EmailAlreadyExists
        if len(username) < 6 or len(username) > 32:
            return StateCode.UsernameInvalid
        if len(password) < 6 or len(password) > 16:
            return StateCode.PasswordInvalid
        code:StateCode = PRTS.TempStringManager.checkVerifyCode(username, verifyCode)
        if code != StateCode.Success:
            return code
        dbCursor = this.DataBase.cursor()
        templatefile = open("./template.json", "r", encoding="utf-8")
        template = templatefile.read()
        templatefile.close()
        dbCursor.execute("INSERT INTO usermeta VALUES (?, ?, ?, ?, ?, ?)", (username, password, nickname, email, str(time.time()), template))
        return StateCode.Success

    def login(this, username:str, password:str)->Tuple[StateCode, str]:
        """
        Login an account.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT password FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None or result[0] != password:
            return StateCode.UsernameOrPasswordNotMatch, ""
        token:str = PRTS.TempStringManager.getToken(username)
        return StateCode.Success, token
    
    def getMetaExpand(this, username:str)->Tuple[StateCode, dict]:
        """
        Get the user meta expand data.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT data, nickname FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UnknownError, ""
        rjson = json.loads(result[0])
        rjson["nickname"] = result[1]
        return StateCode.Success, rjson
    
    def setMetaExpand(this, username:str, data:dict)->StateCode:
        """
        Set the user meta expand data.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT data FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UnknownError
        nickname = data["nickname"]
        data.pop("nickname")
        dbCursor.execute("UPDATE usermeta SET nickname=?, data=? WHERE username=?", (nickname, json.dumps(data), username))
        return StateCode.Success
    
    def getAccountInfo(this, username:str)->Tuple[StateCode, dict]:
        code, data = this.getMetaExpand(username)
        if code != StateCode.Success:
            return code, {}
        nickname = data["nickname"]
        data = data["AccountInfo"]
        data["nickname"] = nickname
        return StateCode.Success, data
    
    def setAccountInfo(this, username:str, data:dict)->StateCode:
        code, dic = this.getMetaExpand(username)
        if code != StateCode.Success:
            return code
        dic["AccountInfo"] = data
        dic["nickname"] = data["nickname"]
        return this.setMetaExpand(username, dic)





