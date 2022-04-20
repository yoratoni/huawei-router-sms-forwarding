from pyostra import pyprint, LogTypes

import os


class CacheSystem:
    CACHE_PATH = os.path.join(os.getcwd(), "cache.txt")
    SMS_DICT = {}
    
    
    @staticmethod
    def add_to_cache(sms: dict) -> dict:
        """Add a unique SMS (dict formatted) into the cache
        and returns the SMS dict if needed (by reference).

        Args:
            sms (dict): Original unique SMS dict.
        """
    
        if sms is not None and "Index" in sms:
            sms_id = sms["Index"]
            CacheSystem.SMS_DICT[sms_id] = sms
            
        return CacheSystem.SMS_DICT
    
    
    @staticmethod
    def save_cache() -> bool:
        """Save the cache into a txt file.
        
        Note:
            Messages are save as full strings with the format [ID] (DATE) SENDER: @CONTENT.
        """
        
        


    @staticmethod
    def load_cache() -> list[str]:
        """_summary_

        Returns:
            list[str]: _description_
        """