from typing import *
from sqlite3 import *
import json
import datetime
from ._TempStringManager import *
from ._EmailHost import *
from ._Config import *
from hashlib import *
import re

class PRTSAccountMetaManager:
    """
    # AccountMetaManager
    ## Table - User Meta
    | username | password | pswd_mode | hash_salt | nickname | email | registed_time | data |
    | -------- | -------- | ----------| ----------| -------- | ----- | ------------- | ---- |
    | Text     | Text     | Text      | Text      | Text     | Text  | Text          | Text |
    * NOTICE: This website is not working in high-performance environment, so using JSON to store user data.
    """
    DataBase: Connection
    DBCursor: Cursor
    DataBasePath: str
    TempStringManager: PRTSTempStringManager
    EmailHost: PRTSEmailHost
    def __init__(this, tempStringManager:PRTSTempStringManager, emailHost:PRTSEmailHost):
        this.TempStringManager = tempStringManager
        this.EmailHost = emailHost
        this.DataBasePath = PRTSConfig.Instance["DataBase"]["FileFolder"] + "/prts_account.db"
        this.DataBase = connect(this.DataBasePath, isolation_level=None, check_same_thread=False)
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("CREATE TABLE IF NOT EXISTS usermeta (username TEXT, password TEXT, pswd_mode TEXT, hash_salt TEXT, \
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
        code, vcode = this.TempStringManager.getVerifyCode(username)
        if code != StateCode.Success:
            return code
        this.EmailHost.sendEmail(email, PRTSConfig.Instance["EmailHost"]["VerifyCodeSubTitle"],
                                    PRTSConfig.Instance["EmailHost"]["VerifyCodeTemplate"].format(
                                        username=username, code=vcode,
                                        create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        expire_time=PRTSConfig.Instance["VerifyCodeExpireTime"]/60
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
        if len(username) < PRTSConfig.Instance["AccountManager"]["AccountLength"]["Min"] or \
            len(username) > PRTSConfig.Instance["AccountManager"]["AccountLength"]["Max"]:
                return StateCode.UsernameInvalid
        if len(password) < PRTSConfig.Instance["AccountManager"]["PasswordLength"]["Min"] or \
            len(password) > PRTSConfig.Instance["AccountManager"]["PasswordLength"]["Max"]:
                return StateCode.PasswordInvalid
        #check account pattern
        if re.match(PRTSConfig.Instance["AccountManager"]["AccountPattern"], username) == None:
            return StateCode.UsernameInvalid
        #check password pattern
        if re.match(PRTSConfig.Instance["AccountManager"]["PasswordPattern"], password) == None:
            return StateCode.PasswordInvalid
        code:StateCode = this.TempStringManager.checkVerifyCode(username, verifyCode)
        if code != StateCode.Success:
            return code
        storage_policy = PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["Storage"]
        hash_salt = ""
        if storage_policy == "SHA256":
            hash_salt = this.TempStringManager.getRandomString(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
            password = sha256((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "SHA512":
            hash_salt = this.TempStringManager.getRandomString(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
            password = sha512((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "MD5":
            hash_salt = this.TempStringManager.getRandomString(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
            password = md5((password + hash_salt).encode()).hexdigest()
        dbCursor = this.DataBase.cursor()
        template = PRTSConfig.Instance["AccountManager"]["TemplateMetaJson"]
        dbCursor.execute("INSERT INTO usermeta VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (username, password, storage_policy, hash_salt,
                                                                            nickname, email, str(time.time()), template))
        return StateCode.Success

    def login(this, username:str, password:str)->Tuple[StateCode, str]:
        """
        Login an account.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT password, pswd_mode, hash_salt FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UsernameOrPasswordNotMatch, ""
        storage_policy = result[1]
        hash_salt = result[2]
        if storage_policy == "SHA256":
            password = sha256((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "SHA512":
            password = sha512((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "MD5":
            password = md5((password + hash_salt).encode()).hexdigest()
        if password != result[0]:
            return StateCode.UsernameOrPasswordNotMatch, ""
        token:str = this.TempStringManager.getToken(username)
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





