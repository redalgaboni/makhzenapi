from typing import Optional,Tuple
from sqlalchemy.orm import Session
from backend.app.db.models import Jihate, Woulate, AmalateJamaate
from typing import Set

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

def get_amala_id_from_name(db, amala):
    amala_match = db.query(AmalateJamaate).filter(AmalateJamaate.amala_jamaa.contains(amala)).first()

    if amala_match:
        return amala_match.amala_jamaa_id


# check comment doesn't contain insults for endpoing /woulate/{woulate_id}/comment
def load_insult_words() -> Set[str]:
    """Load insult words in Arabic, English, French, and Spanish."""
    # Arabic
    arabic_insults = {
        'زب','الزب','الطبون','طبون', 'زبوبة',
        'قحبة', 'قحاب','القحاب','زمل','زامل','الزامل','زوامل','الزوامل','قواويد',
        'كسم','طبابن','كسك','كسك يا','شرموط','الشرموط','الشرموطة','شرموطة',
        'زبي','زبك','العن ربك','طيزي','طيز','الطيز','زك','زكك','زكوكة','الزكوكة',

        }
    
    # English
    english_insults = {
        "bitch", "whore", "slut", "fuck","fucker",
        "motherfucker", "ass", "asshole", "assholes", "asshole", "assholes",
        "dick", "dickhead", "dickheads", "pussy","cunt",

    }
    
    # French
    french_insults = {
        "salaud","pute", "salope", "enculé","merde","bordel",
        "salopard", "nique", "ta queule", "espèce de", "bite", "ma queue",
        "fils de chien","putain","putaine",
        "saloperie"
    }
    
    # Spanish
    spanish_insults = {
        "gilipollas", "cabrón", "zorra",
        "canalla", "payaso","maricón","joder","mierda",
        "coño","pendejo","culero","chingar","chinga tu madre",
        "hijo de puta","maldito","maldita","mierda","puta","puto",
    }
    
    # Combine and normalize to lowercase
    all_insults = set()
    for word in arabic_insults | english_insults | french_insults | spanish_insults:
        all_insults.add(word.lower())
    
    return all_insults



def contains_insults(comment: str) -> bool:
    """
    Check if the comment contains any insults from the insults_list.
    """

    comment_lower = comment.lower()
    insults_list = load_insult_words()
    for insult in insults_list:
        if insult in comment_lower:
            return True
    return False

def extract_job_title(description: str) -> str:
    """Extract generic title from description (e.g., 'عامل مكلف...' -> 'عامل')"""
    if "والي" in description:
        return "والي"
    elif "عامل" in description:
        return "عامل"
    elif "مدير" in description:
        return "مدير"
    else:
        return "غير محدد"

def deactivate_previous_assignments(db: Session, full_name: str):
    """
    Mark all previous assignments for this person as inactive and also
    if same wilaya_id exists with another active person
    
    """
    db.query(Woulate).filter(
        (Woulate.full_name == full_name,Woulate.active == True) or
        (Woulate.wilaya_id == Woulate.wilaya_id, Woulate.active == True)
    ).update({"active": False})