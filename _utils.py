from typing import *
from enum import *
import random, os

class PRTS:
    AccountManager:Any = None
    TempStringManager:Any = None
    EmailHost:Any = None
    AccountMetaTemplateJson:str = \
"""
{
  "AccountInfo":{
    "TEL": "",
    "TELPrefix": "",
    "Gender": "",
    "Brief": ""
  },
  "Privacy":{
    "Name": "",
    "ID": ""
  },
}
"""
    EmailTitle:str = "PRTS"
    EmailVerifyCodeSubTitle:str = "Verify Code"
    EmailHostAddress:str = ""
    EmailHostPort:int = 465
    EmailAccount:str = ""
    EmailPassword:str = ""
    EmailVerifyCodeTemplate:str = \
"""
尊敬的用户{username}，您好！
您于 {create_time} 申请的验证码是：{code}，请在{expire_time}分钟内完成验证。
"""
    def __init__(this):
        pass

    @staticmethod
    def generateRandomChar()->str:
        rNum = chr(random.randint(48, 57))
        rChar = chr(random.randint(65, 90))
        if rChar=="I":rChar="V"
        if rChar=="O":rChar="M"
        if rChar=="D":rChar="A"
        if rChar=="L":rChar="B"
        if random.randint(0,1):
            return rNum
        else:
            return rChar
    
    @staticmethod
    def getRandomStr(length:int)->str:
        result = ""
        for i in range(length):
            result += PRTS.generateRandomChar()
        return result
    
    @staticmethod
    def getSizeOfFolder(folder:str)->int:
        total_size = 0
        for path, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(path, file)
                total_size += os.path.getsize(file_path)
        return total_size

class StateCode(Enum):
    UnknownError = 0
    Success = 1
    PermissionDenied = 2
    UsernameAlreadyExists = 100
    EmailAlreadyExists = 101
    VerifyCodeNotMatch = 102
    VerifyCodeNotExpired = 103
    UsernameOrPasswordNotMatch = 104
    UnknwonUsername = 105
    UsernameInvalid = 200
    PasswordInvalid = 201
    EmailInvalid = 202
    VerifyCodeInvalid = 203
    VerifyCodeExpired = 204
    TokenExpired = 205
    WorkIDNotExist = 300
    FileTypeInvalid = 301
    NoTraceOpened = 302
    FileTooLarge = 303
    StorageNotEnough = 304
    LevelNotOpened = 305
    NotCurrentSeason = 400
    SeasonNotStarted = 401
    UnknownTrace = 402
    UnknownLevel = 403
    TraceConflict = 404
    RootNotExist = 800
    RootAlreadyExist = 801
    LengthMustMoreThanTwo = 802
    ResourceNotExist = 900
    ResourceAlreadyExist = 901
    SubmitTooFast = 902
    
class Permissons(Enum):
    Site_Admin = "Site.Admin"
    Site_User = "Site.User"
    Site_Forbidden = "Site.Forbidden"
    