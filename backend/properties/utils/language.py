from base_config.settings import LANGUAGE_CODE
from properties.models import Language


def get_default_language() -> Language:
    """
    Retrieve the default language from the database, or create it if it does not exist.

    This function ensures that a Language object with the code defined in LANGUAGE_CODE
    exists. If it does not exist, it will be created with the following defaults:
        - code: LANGUAGE_CODE (defined in the settings file)
        - name='English (American)'
        - code='en-us'

    Returns:
        Language: An instance of the Language model representing the default language.
    """
    instance, _ = Language.objects.get_or_create(code=LANGUAGE_CODE, name='English (American)')
    return instance
