from typing import *
from sqlite3 import *
import json
import datetime
from ._TempStringManager import *
from ._Config import *
from hashlib import *
import re

class PRTSVerifyCodeSender:
    def __init__(this):
        pass

    def onVerifyCode(this, username:str, email:str, accountInfo:dict, verifyCode:str)->StateCode:
        """
        Send the verify code to the email.
        """
        print("Warning: The verify code sender is not set. Verify code (" + verifyCode + ") for " + username + " is not sent.")
        return StateCode.UnknownError

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
    VerifyCodeSender: PRTSVerifyCodeSender
    Instance: 'PRTSAccountMetaManager' = None
    def __init__(this, tempStringManager:PRTSTempStringManager):
        if PRTSAccountMetaManager.Instance != None:
            raise Exception("PRTSAccountMetaManager is a singleton class.")
        this.TempStringManager = tempStringManager
        this.VerifyCodeSender = PRTSVerifyCodeSender()
        this.DataBasePath = PRTSConfig.Instance["DataBase"]["FileFolder"] + "/prts_account.db"
        this.DataBase = connect(this.DataBasePath, isolation_level=None, check_same_thread=False)
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("CREATE TABLE IF NOT EXISTS usermeta (username TEXT, password TEXT, pswd_mode TEXT, hash_salt TEXT, \
nickname TEXT, email TEXT, registed_time TEXT, data TEXT)")
        PRTSAccountMetaManager.Instance = this

    def setVerifyCodeSender(this, sender:PRTSVerifyCodeSender):
        this.VerifyCodeSender = sender

    def checkAccountRegistered(this, username:str)->bool:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT username FROM usermeta WHERE username=?", (username,))
        return dbCursor.fetchone() != None
    
    def checkEMailBindLimit(this, email:str)->int:
        limit = PRTSConfig.Instance["AccountManager"]["EmailBindLimit"]
        if limit < 1:
            return -1
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT email FROM usermeta WHERE email=?", (email,))
        binded = len(dbCursor.fetchall())
        return limit - binded
    
    def sendVerifyCode(this, username:str, email:str = "")->StateCode:
        """
        Send a verify code to the email.
        If the email is empty, it will get the email from the database.
        Which means this function can be used both in the register process and the password reset process.
        """
        if email == "":
            dbCursor = this.DataBase.cursor()
            dbCursor.execute("SELECT email FROM usermeta WHERE username=?", (username,))
            email = dbCursor.fetchone()
            if email == None:
                return StateCode.UnknownError
            email = email[0]
            code, vcode = this.TempStringManager.getVerifyCode(username)
            if code != StateCode.Success:
                return code
            if this.VerifyCodeSender != None:
                return this.VerifyCodeSender.onVerifyCode(username, email, this.getMetaExpand(username), vcode)
        else:
            code, vcode = this.TempStringManager.getVerifyCode(username)
            if code != StateCode.Success:
                return code
            return this.VerifyCodeSender.onVerifyCode(username, email, {}, vcode)
        return StateCode.UnknownError

    def register(this, username:str, password:str, email:str, nickname:str)->(StateCode):
        """
        Register a new account.
        email: just same as the email that received the verify code.
        nickname: any string, even empty, but length should be less than 32.
        """
        if this.checkAccountRegistered(username):
            return StateCode.UsernameAlreadyExists
        if this.checkEMailBindLimit(email) == 0:
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
        storage_policy:str = PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["Storage"]
        hash_salt = ""
        if storage_policy == "SHA256":
            hash_salt = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
            password = sha256((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "SHA512":
            hash_salt = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
            password = sha512((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "MD5":
            hash_salt = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
            password = md5((password + hash_salt).encode()).hexdigest()
        dbCursor = this.DataBase.cursor()
        template = PRTSConfig.Instance["AccountManager"]["TemplateMetaJson"]
        dbCursor.execute("INSERT INTO usermeta VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (username, password, storage_policy, hash_salt,
                                                                            nickname, email, str(time.time()), template))
        return StateCode.Success

    def login(this, username:str, password:str)->StateCode:
        """
        Login an account.
        Return the token if success.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT password, pswd_mode, hash_salt FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UsernameOrPasswordNotMatch
        storage_policy:str = result[1]
        hash_salt:str = result[2]
        if storage_policy == "SHA256":
            password = sha256((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "SHA512":
            password = sha512((password + hash_salt).encode()).hexdigest()
        elif storage_policy == "MD5":
            password = md5((password + hash_salt).encode()).hexdigest()
        if password != result[0]:
            return StateCode.UsernameOrPasswordNotMatch
        return StateCode.Success
    
    def changePassword(this, username:str, newPassword:str)->StateCode:
        """
        Change the password of an account.
        Notice: this function will not check the old password. Should be used with getVerifyCode, and check the verify code.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT password, pswd_mode, hash_salt FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UnknownError
        storage_policy = PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["Storage"]
        hash_salt = PRTSUtils.getRandomStr(PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["HashModeSaltLength"])
        if storage_policy == "SHA256":
            newPassword = sha256((newPassword + hash_salt).encode()).hexdigest()
        elif storage_policy == "SHA512":
            newPassword = sha512((newPassword + hash_salt).encode()).hexdigest()
        elif storage_policy == "MD5":
            newPassword = md5((newPassword + hash_salt).encode()).hexdigest()
        dbCursor.execute("UPDATE usermeta SET password=? WHERE username=?", (newPassword, username))
        return StateCode.Success
    
    def enhancePlainPassword(this):
        """
        Enhance the plain password to current storage policy.
        If current storage policy is plain, it will do nothing.
        """
        if PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["Storage"] == "PLAIN":
            return
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT username, password, hash_salt FROM usermeta")
        result = dbCursor.fetchall()
        for row in result:
            username = row[0]
            password = row[1]
            hash_salt = row[2]
            storage_policy = PRTSConfig.Instance["AccountManager"]["PasswordPolicy"]["Storage"]
            if storage_policy == "SHA256":
                password = sha256((password + hash_salt).encode()).hexdigest()
            elif storage_policy == "SHA512":
                password = sha512((password + hash_salt).encode()).hexdigest()
            elif storage_policy == "MD5":
                password = md5((password + hash_salt).encode()).hexdigest()
            dbCursor.execute("UPDATE usermeta SET password=?, pswd_mode=?, hash_salt=? WHERE username=?", (password, storage_policy, hash_salt, username))

    def getNickname(this, username:str)->str:
        """
        Get the nickname of the user.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT nickname FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return ""
        return result[0]
    
    def setNickname(this, username:str, nickname:str)->StateCode:
        """
        Set the nickname of the user.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("UPDATE usermeta SET nickname=? WHERE username=?", (nickname, username))
        return StateCode.Success
    
    def getMetaExpand(this, username:str)->Tuple[StateCode, dict]:
        """
        Get the user meta expand data.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT data FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UnknownError, ""
        return StateCode.Success, json.loads(result[0])
    
    def setMetaExpand(this, username:str, data:dict)->StateCode:
        """
        Set the user meta expand data.
        """
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT data FROM usermeta WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.UnknownError
        dbCursor.execute("UPDATE usermeta SET data=? WHERE username=?", (json.dumps(data), username))
        return StateCode.Success