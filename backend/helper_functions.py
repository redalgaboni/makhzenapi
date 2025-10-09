from typing import Optional,Tuple
from sqlalchemy.orm import Session
from backend.app.db.models import Jihate

# Helper function to get jiha_id from location name
def get_jiha_id_from_location(db: Session, location: str) -> Optional[Tuple[int, str]]:
    """
    Get jiha_id by matching location name against:
    - jihate.jiha (جهة names)
    """

    # jiha string contains location
    jiha_match = db.query(Jihate).filter(Jihate.jiha.contains(location)).first()
    
    if jiha_match:
        return jiha_match.jiha_id, jiha_match.jiha
    
    return None

def get_wilaya_name(db: Session, wilaya_id: int) -> str:

    wilaya_match = db.query(Jihate).filter(Jihate.wilaya_id == wilaya_id).first()

    if wilaya_match:
        return wilaya_match.wilaya
    
    return None