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
    AccountLength:
        Min: 6
        Max: 32
    PasswordLength:
        Min: 6
        Max: 16
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

    def saveConfig(this):
        with open(this.defaultYAMLPath, "w", encoding="utf-8") as f:
            yaml.dump(this.config, f, allow_unicode=True)

    def reloadConfig(this):
        this.loadConfig()

    def __getitem__(this, key):
        return this.config[key]
    
    def __setitem__(this, key, value):
        this.config[key] = value
                