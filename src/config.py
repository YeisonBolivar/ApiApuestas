class Config:
    SECRET_KEY = 'secret_key'
    

class DevelopmentConfig(Config):
    DEBUG = True


config = {
    "development": DevelopmentConfig
}
