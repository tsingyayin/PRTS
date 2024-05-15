import yaml
import os
class PRTSConfig:
    Instance: 'PRTSConfig' = None
    defaultYAMLStr: str = \
"""# PRTS Configuration File
DataBase:
    FileFolder: "./db"
AccountManager:
    TemplateMetaJson: |
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
    AccountPolicy:
        # Pattern : generally, recommend a-z,A-Z,0-9 and _.
        Pattern: "^[a-zA-Z0-9_]+$"
        MinLength: 6
        MaxLength: 32
    PasswordPolicy: 
        # Pattern : generally, recommend a-z,A-Z,0-9, The symbol corresponding to 1-9 on the keyboard after shift(eg. !@#$%^&*()_+)
        Pattern: "^[a-zA-Z0-9!@#$%^&*()_+]+$"
        MinLength: 6
        MaxLength: 16
        # Storage: PLAIN, SHA256, SHA512, MD5
        # We recommend using SHA256 or SHA512, but PLAIN is more convenient for debugging.
        Storage: "PLAIN"
        HashModeSaltLength: 16
    EmailBindLimit: 1 # any value less than 1 means no limit. not recommended.
    VerifyCodeLength: 6
    VerifyCodeExpireTime: 600 # seconds (10 minutes)
    TokenLength: 32
    TokenExpireTime: 604800 # seconds (7 days)
    
EmailHost:
    HostAddress: ""
    HostPort: 465
    Account: ""
    Password: ""
    Title: "PRTS"
    VerifyCodeSubTitle: "Verify Code"
    VerifyCodeTemplate: |
        尊敬的用户{username}，您好！
        您于 {create_time} 申请的验证码是：{code}，请在{expire_time}分钟内完成验证。

ProductKey:
    Part: 4
    Length: 5 # xxxxx-xxxxx-xxxxx-xxxxx
"""

    def __init__(this, defaultYAMLPath: str = "./PRTS.yaml"):
        if PRTSConfig.Instance == None:
            this.defaultYAMLPath = defaultYAMLPath
            this.config:dict = {}
            this.loadConfig()
            PRTSConfig.Instance = this
        

    def loadConfig(this):
        try:
            with open(this.defaultYAMLPath, "r", encoding="utf-8") as f:
                this.config = yaml.load(PRTSConfig.defaultYAMLStr, Loader=yaml.FullLoader)
                this.config.update(yaml.load(f.read(), Loader=yaml.FullLoader))
        except:
            this.config = yaml.load(PRTSConfig.defaultYAMLStr, Loader=yaml.FullLoader)
            with open(this.defaultYAMLPath, "w", encoding="utf-8") as f:
                f.write(PRTSConfig.defaultYAMLStr)

        if not os.path.exists(this["DataBase"]["FileFolder"]):
            os.makedirs(this["DataBase"]["FileFolder"])


    def reloadConfig(this):
        this.loadConfig()

    def __getitem__(this, key):
        return this.config[key]
    
    def __setitem__(this, key, value):
        this.config[key] = value
                