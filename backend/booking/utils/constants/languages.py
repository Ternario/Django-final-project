class LanguageConfig:
    SUPPORTED_LANGUAGES = {'en': 'English', 'de': 'Deutsch'}
    BLACKLIST_WORDS = {
        'en': ['spam', 'fraud'],
        'de': ['spam', 'betrug']
    }


class Moderator:
    def __init__(self):
        self.config = LanguageConfig()
