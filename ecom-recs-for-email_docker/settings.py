# settings for the model training and prediction
class Settings:
    NO_COMPONENTS = 10
    LEARNING_RATE = 0.05
    LOSS = "warp"
    EPOCHS = 4
    K = 10
    K_SPARE = K * 3
    CHUNK = 10000
