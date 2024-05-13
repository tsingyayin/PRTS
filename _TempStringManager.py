from typing import *
from sqlite3 import *
from ._utils import *
import time

class VITempStringManager:
    """
    # verifycode
    | username | code | ttl | spawn_time |
    | -------- | ---- | --- | ---------- |
    | Text     | Text | Int | Int        |
    # token
    | username | token | ttl | spawn_time |
    | -------- | ----- | --- | ---------- |
    | Text     | Text  | Int | Int        |
    # permission_group
    | groupname | permission | ttl |
    | --------- | ---------- | --- |
    | Text      | Text       | Int |
    # permission
    | username | permission | ttl | spawn_time |
    | -------- | ---------- | --- | ---------- |
    | Text     | Text       | Int | Int        |
    """
    DataBasePath: str
    DataBase: Connection
    DBCursor: Cursor
    def __init__(this, DataBasePath: str = "./db/temporary.db"):
        PRTS.TempStringManager = this
        this.DataBasePath = DataBasePath
        this.DataBase = connect(DataBasePath, isolation_level=None, check_same_thread=False)
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS verifycode \
(username TEXT, code TEXT, ttl INTEGER, spawn_time INTEGER)")
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS token \
(username TEXT, token TEXT, ttl INTEGER, spawn_time INTEGER)")
        this.DataBase.execute("CREATE TABLE IF NOT EXISTS permission \
(username TEXT, permission Text, ttl INTEGER, spawn_time INTEGER)")
    
    def getVerifyCode(this, username:str)->Tuple[StateCode, str]:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT code, ttl, spawn_time FROM verifycode WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM verifycode WHERE username=?", (username,))
        VCode:str = PRTS.getRandomStr(8)
        dbCursor.execute("INSERT INTO verifycode VALUES (?, ?, ?, ?)", (username, VCode, 600, time.time()))
        return StateCode.Success, VCode
    
    def checkVerifyCode(this, username:str, verifyCode:str)->(StateCode):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT code, ttl, spawn_time FROM verifycode WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.VerifyCodeExpired
        if result[0] != verifyCode:
            return StateCode.VerifyCodeNotMatch
        if result[2] + result[1] < time.time():
            dbCursor.execute("DELETE FROM verifycode WHERE username=?", (username,))
            return StateCode.VerifyCodeExpired
        else:
            dbCursor.execute("DELETE FROM verifycode WHERE username=?", (username,))
            return StateCode.Success
    
    def getToken(this, username:str)->(str):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM token WHERE username=?", (username,))
        Token:str = PRTS.getRandomStr(32)
        dbCursor.execute("INSERT INTO token VALUES (?, ?, ?, ?)", (username, Token, 604800, time.time()))
        return Token
    
    def checkToken(this, username:str, token:str)->Tuple[StateCode, str]:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT token, ttl, spawn_time FROM token WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.TokenExpired, ""

        if result[2] + result[1] < time.time():
            return StateCode.TokenExpired, ""
        else:
            # remove the old token
            if result[0] != token:
                return StateCode.TokenExpired, ""
            dbCursor.execute("DELETE FROM token WHERE username=?", (username,))
        Token:str = PRTS.getRandomStr(32)
        dbCursor.execute("INSERT INTO token VALUES (?, ?, ?, ?)", (username, Token, 604800, time.time()))
        return StateCode.Success, Token
    
    def tokenAuth(this, username:str, token:str)->(StateCode):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT token, ttl, spawn_time FROM token WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return StateCode.TokenExpired
        if result[0] != token:
            return StateCode.TokenExpired
        if result[2] + result[1] < time.time():
            return StateCode.TokenExpired
        else:
            dbCursor.execute("UPDATE token SET spawn_time=? WHERE username=?", (time.time(), username))
            return StateCode.Success
        
    def clearExipred(this):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM verifycode WHERE spawn_time + ttl < ?", (time.time(),))
        dbCursor.execute("DELETE FROM token WHERE spawn_time + ttl < ?", (time.time(),))

    def refreshLastSubmit(this, username:str):
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT last_submit FROM urrs_last_submit WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            dbCursor.execute("INSERT INTO urrs_last_submit VALUES (?, ?)", (username, time.time()))
        else:
            dbCursor.execute("UPDATE urrs_last_submit SET last_submit=? WHERE username=?", (time.time(), username))

    def getLastSubmit(this, username:str)->int:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT last_submit FROM urrs_last_submit WHERE username=?", (username,))
        result = dbCursor.fetchone()
        if result == None:
            return 0
        return result[0]
    
    def isUserSubmitTooFast(this, username:str)->bool:
        last_submit = this.getLastSubmit(username)
        if last_submit + 10 > time.time():
            return True
        return False
    
    def addPermissionForGroup(this, groupname:str, permission:str, ttl:int)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl \
FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        dbCursor.execute("INSERT INTO permission_group VALUES (?, ?, ?)", (groupname, permission, ttl))
        return StateCode.Success
    
    def removePermissionForGroup(this, groupname:str, permission:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        return StateCode.Success
    
    def checkPermissionForGroup(this, groupname:str, permission:str, spawn_time:int)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl \
FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
        result = dbCursor.fetchone()
        if result == None:
            # 获取此权限组中的所有以"group."开头的权限为组名，以递归的方式检查权限
            dbCursor.execute("SELECT permission, ttl FROM permission_group \
WHERE groupname=? AND permission LIKE 'group.%'", (groupname,))
            result = dbCursor.fetchall()
            for i in result:
                if this.checkPermissionForGroup(i[0][6:], permission, spawn_time) == StateCode.Success:
                    return StateCode.Success
            return StateCode.PermissionDenied
        if result[0] + spawn_time < time.time():
            dbCursor.execute("DELETE FROM permission_group WHERE groupname=? AND permission=?", (groupname, permission))
            return StateCode.PermissionDenied
        return StateCode.Success
        
    def checkPermission(this, username:str, permission:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl, spawn_time \
FROM permission WHERE username=? AND permission=?", (username, permission))
        result = dbCursor.fetchone()
        if result == None:
            dbCursor.execute("SELECT permission, ttl, spawn_time FROM permission \
WHERE username=? AND permission LIKE 'group.%'", (username,))
            result = dbCursor.fetchall()
            for i in result:
                if this.checkPermissionForGroup(i[0][6:], permission, i[2]) == StateCode.Success:
                    return StateCode.Success
            return StateCode.PermissionDenied
        if result[1] + result[0] < time.time():
            dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, permission))
            return StateCode.PermissionDenied
        return StateCode.Success
    
    def addPermission(this, username:str, permission:str, ttl:int)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl, spawn_time \
FROM permission WHERE username=? AND permission=?", (username, permission))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, permission))
        dbCursor.execute("INSERT INTO permission VALUES (?, ?, ?, ?)", (username, permission, ttl, time.time()))
        return StateCode.Success
    
    def removePermission(this, username:str, permission:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, permission))
        return StateCode.Success
    
    
    def addPermissionGroup(this, username:str, groupname:str)->StateCode:
        dbCursor = this.DataBase.cursor()
        dbCursor.execute("SELECT ttl, spawn_time \
FROM permission WHERE username=? AND permission=?", (username, "group."+groupname))
        result = dbCursor.fetchone()
        if result != None:
            dbCursor.execute("DELETE FROM permission WHERE username=? AND permission=?", (username, "group."+groupname))
        dbCursor.execute("INSERT INTO permission VALUES (?, ?, ?, ?)", (username, "group."+groupname, 0, time.time()))
        return StateCode.Success
    