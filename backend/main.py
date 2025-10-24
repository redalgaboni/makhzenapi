from fastapi import Depends, FastAPI, HTTPException, Query, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.db.session import SessionLocal, get_db
from backend.app.db.models import Jihate, AmalateJamaate, Woulate, User, Reaction, Comment
from backend.app.core.config import settings
from sqlalchemy.orm import Session
from backend.helper_functions import get_jiha_id_from_location, get_wilaya_name, \
    contains_insults, extract_job_title
from backend.app.core.security import create_access_token, verify_password,get_user,get_current_user
from datetime import timedelta
from typing import List, Union,Optional
from .pydantic_models import WoulatDetailResponse, ReactionCreate, CommentCreate,\
    ReactionResponse, CommentResponse, WoulateCreate, WoulateSearchResult
import logging,json
from sqlalchemy.sql.expression import or_

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

logger = logging.getLogger("app")

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
    ) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action"
        )
    return current_user

####### FastAPI Application Setup #######
app = FastAPI(
    title="Makhzen API",
    description="Returns Jihate, Wilaya, Amalate/Mukataate, Woulate data from Makhzen database",
    version="0.1",
    #terms_of_service="http://example.com/terms/",
    contact={
        "name": "Reda lgaboni",
        "url": "https://sorakobra.com/about",
        "email": "redalgaboni@tutamail.com",
    },
    #license_info={
    #    "name": "Apache 2.0",
    #    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    #},
    #openapi_tags=tags_metadata
    #docs_url="/documentation"
              )

@app.get("/", tags=["Root"])
async def root(
    current_user: User = Depends(get_current_user)
    ):
    return {"message": "Welcome to the Makhzen API"}

@app.post("/login", tags=["Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/info", tags=["Info"])
async def info(
    current_user: User = Depends(get_current_user)
    ):
    return {"app_name": settings.APP_NAME, "version": settings.VERSION}

@app.get("/health", tags = ["Info"])
async def health_check():
    logger.debug("Health check")
    return {"status": "ok"}

#call to return all jihate names and ids
@app.get("/jihate", tags=["Search"])
def get_all_jihate(
    current_user: User = Depends(get_current_user)
    ):
    """
    Get all jihate names and ids.
    Returns a list of jiha objects with their ids.
    """
    db = SessionLocal()
    logger.debug("JIHATI")
    try:
        jihate = db.query(Jihate).distinct(Jihate.jiha_id, Jihate.jiha).all()
        return [
            {
                "jiha_id": j.jiha_id,
                "jiha": j.jiha
            }
            for j in jihate
        ]
    finally:
        db.close()


@app.get("/jiha", tags=["Search"])
def get_jiha_details(
    locations: List[str] = Query(..., description="List of location names (e.g., ['الرباط', 'فاس', 'جهة الشرق'])"),
    current_user: User = Depends(get_current_user)
    ):
    """
    Get all wilayas for multiple jihate by location names.
    Returns a list of jiha objects with their wilayas.
    """
    db = SessionLocal()
    try:
        results = []
        processed_jiha_ids = set() 

        for location in locations:
            jiha_info = get_jiha_id_from_location(db, location)
            
            if jiha_info is None:
                # Skip invalid locations
                continue
                
            jiha_id, jiha_name = jiha_info
            
            # Skip if we already processed this jiha_id
            if jiha_id in processed_jiha_ids:
                continue
                
            processed_jiha_ids.add(jiha_id)
            
            # Get all wilayas for this jiha_id
            wilayas = db.query(Jihate).filter(Jihate.jiha_id == jiha_id).all()
            
            results.append({
                "jiha": jiha_name,
                "jiha_id": jiha_id,
                "wilayas": [
                    {
                        "wilaya_id": w.wilaya_id,
                        "wilaya": w.wilaya,

                    }
                    for w in wilayas
                ]
            })
        
        if not results:
            raise HTTPException(
                status_code=404, 
                detail=f"No valid locations found among: {locations}"
            )
        
        return results
        
    finally:
        db.close()

@app.get("/amala_jamaa", tags=["Search"])
def get_amala_jamaa(
    locations: List[str] = Query(..., description="List of location names (e.g., ['الرباط', 'فاس', 'جهة الشرق'])"),
    current_user: User = Depends(get_current_user)
):
    """
    Get amalate/mukataate by locations names.
    Returns amala_jamaa and wilaya for all subdivisions for each matching jiha.
    """
    db = SessionLocal()
    try:
        results = []
        processed_jiha_ids = set()
        
        for location in locations:
            # Get jiha_id and jiha name by matching location name
            jiha_info = get_jiha_id_from_location(db, location)
            
            if jiha_info is None:
                # Skip invalid locations
                continue
                
            jiha_id, jiha_name = jiha_info
            
            # Skip if we already processed jiha_id
            if jiha_id in processed_jiha_ids:
                continue
            
            processed_jiha_ids.add(jiha_id)
            
            # Get all amalate_jamaa for this jiha
            amalate = db.query(AmalateJamaate).filter(AmalateJamaate.jiha_id == jiha_id).all()
            
            # Only include if amalate exist
            if amalate:
                results.append({
                    "jiha": jiha_name,
                    "jiha_id": jiha_id,
                    "amalate_jamaa": [
                        {
                            "amala_jamaa": a.amala_jamaa,
                            "amala_jamaa_id": a.amala_jamaa_id,
                            "wilaya": a.wilaya,
                            "wilaya_id": a.wilaya_id
                        }
                        for a in amalate
                    ]
                })
        
        # Return results (empty list if no matches found)
        if not results:
            raise HTTPException(
                status_code=404, 
                detail=f"No amalate/mukataate found for locations: {locations}"
            )
        
        return results
        
    finally:
        db.close()

@app.get("/woulate", tags=["Search"])
def get_woulate(
    location: str = Query(..., description="Location name (e.g., 'الرباط', 'فاس')"),
    active: bool = True,
    current_user: User = Depends(get_current_user)
    ):
    """
    Get woulat by location name and active status.
    Returns jiha, wilaya (from amalate_jamaate or jihate), job details for all matching appointments.
    """
    db = SessionLocal()
    try:
        jiha_id,jiha = get_jiha_id_from_location(db, location)
        if jiha_id is None:
            raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
        
        wilayas = db.query(Woulate).filter(Woulate.jiha_id == jiha_id).all()
        if not wilayas:
            raise HTTPException(status_code=404, detail=f"No wilayas found for jiha_id {jiha_id}")
        

        # if active = True return only records that are active, else return all
        if active:
            wilayas = [w for w in wilayas if w.active]
        # Return json with jiha as primary key and list of wilayas
        return {
            "jiha": jiha,
            "jiha_id": jiha_id,
            "woulate": [
                {    
                    "woulate_id": w.id,
                    "wilaya": get_wilaya_name(db, w.wilaya_id),
                    "wilaya_id": w.wilaya_id,
                    "amala_jamaa": w.amala,
                    "amala_jamaa_id": w.amala_jamaa_id,
                    "idara": w.idara,
                    "full_name": w.full_name,
                    "job_title": w.job_title,
                    "job_description": w.job_description,
                    "active": w.active,
                    "assignment_date": w.assignment_date,
                    "assignment_year": w.assignment_year
                }
                for w in wilayas
            ]
        }
    
    finally:
        db.close()

@app.post("/woulate/{woulate_id}/react", response_model=ReactionResponse, tags=["Reactions"])
def react_to_woulate(
    woulate_id: int,
    reaction: ReactionCreate,
    current_user: User = Depends(get_current_user)
    ):
    """Add or update a reaction to a woulat."""
    
    db = SessionLocal()
    # Verify woulat exists
    woulat = db.query(Woulate).filter(Woulate.id == woulate_id).first()
    if not woulat:
        raise HTTPException(status_code=404, detail="Woulat not found")
    
    # Check if user already reacted
    existing_reaction = db.query(Reaction).filter(
        Reaction.woulate_id == woulate_id,
        Reaction.user_id == current_user.id
    ).first()
    
    if existing_reaction:
        # Update existing reaction
        existing_reaction.reaction_type = reaction.reaction_type
        db.commit()
        db.refresh(existing_reaction)
        return existing_reaction
    else:
        # Create new reaction
        new_reaction = Reaction(
            woulate_id=woulate_id,
            user_id=current_user.id,
            reaction_type=reaction.reaction_type
        )
        db.add(new_reaction)
        db.commit()
        db.refresh(new_reaction)
        return new_reaction

@app.post("/woulate/{woulate_id}/comment", response_model=CommentResponse, tags=["Reactions"])
def comment_on_woulate(
    woulate_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user)
    ):
    """
    Add a comment to a woulat
    """
    db = SessionLocal()

    # Check for insults
    logger.debug(comment.content)

    if contains_insults(comment.content):
        raise HTTPException(
            status_code=400,
            detail="Comment contains inappropriate language"
        )
        
    # Verify woulat exists
    woulate = db.query(Woulate).filter(Woulate.id == woulate_id).first()
    if not woulate:
        raise HTTPException(status_code=404, detail="Woulat not found")
    
    # Create comment
    new_comment = Comment(
        woulate_id=woulate_id,
        user_id=current_user.id,
        content=comment.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.get("/woulate/search", response_model=List[WoulateSearchResult], tags=["Search"])
def search_woulate(
    q: str = Query(..., min_length=2 ,description="Search term (min 2 chars)"),
    active: bool = True,
    current_user: User = Depends(get_current_user)
    ):
    """
    Search woulat by name, job title, wilaya, or jiha (case-insensitive, partial match).
    Supports Arabic, French, English.
    """
    db = SessionLocal()

    # Normalize search term
    search_term = f"%{q}%"
    logger.debug("Search term: %s", search_term)

    # Join with jihate to get jiha/wilaya names
    results = (
        db.query(Woulate, Jihate.jiha, Jihate.wilaya)
        .join(Jihate, 
              (Woulate.jiha_id == Jihate.jiha_id) & 
              (Woulate.wilaya_id == Jihate.wilaya_id))
        .filter(
            or_(
                Woulate.full_name.ilike(search_term),
                Woulate.job_title.ilike(search_term),
                Woulate.job_description.ilike(search_term),
                Woulate.amala.ilike(search_term),
                Jihate.wilaya.ilike(search_term),
                Jihate.jiha.ilike(search_term),
            )
        )
        .limit(20)  # Prevent excessive results
        .all()
    )
    logger.info("Search results: %s", results)
    
    db.close()

    if active:
        results = [(w, jiha, wilaya) for w, jiha, wilaya in results if w.active]

    logger.info('results: %s', results)
    # Format response
    return [
        WoulateSearchResult(
            id=w.id,
            full_name=w.full_name,
            job_title=w.job_title,
            job_description=w.job_description, 
            jiha=jiha,
            wilaya=wilaya,
            amala=w.amala if w.amala else "",
            assignment_date=w.assignment_date if w.assignment_date else None, 
            assignment_year=w.assignment_year,
            active=w.active
        )
        for w, jiha, wilaya in results
        ]

@app.get("/woulate/{woulate_id}", response_model=WoulatDetailResponse, tags=["Reactions"])
def get_woulate_detail(
    woulate_id: int,
    current_user: User = Depends(get_current_user)
    ):
    """Get woulat details with reactions and comments."""
    db = SessionLocal()
    woulate = db.query(Woulate).filter(Woulate.id == woulate_id).first()
    if not woulate:
        raise HTTPException(status_code=404, detail="Woulat not found")
       
    # Get reactions and comments
    reactions = db.query(Reaction).filter(Reaction.woulate_id == woulate_id).all()
    comments = db.query(Comment).filter(
        Comment.woulate_id == woulate_id,
        Comment.is_deleted == False
    ).all()
    
    return WoulatDetailResponse(
        id=woulate.id,
        full_name=woulate.full_name,
        job_title=woulate.job_title,
        job_description=woulate.job_description,
        reactions=reactions,
        comments=comments
    )
      
@app.post("/woulate", response_model=Union[WoulateSearchResult, List[WoulateSearchResult]],
           tags=["Admin"])
def create_woulate(
    woulate_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Add a new woulat record (admin only)
    Accepts jiha/wilaya names and resolves them to IDs
    Automatically deactivates anterior assignments for the same person
    """
    woulate_list = []
    if file:
        file_contents = file.file.read()
        data = json.loads(file_contents.decode('utf-8'))
        if not isinstance(data, list):
            data = [data] 
        for item in data:
            woulate_list.append(WoulateCreate.model_validate(item))


    elif woulate_input:
        data = json.loads(woulate_input)

        if isinstance(data, list):
            for item in data:
                woulate_list.append(WoulateCreate.model_validate(item))
        elif isinstance(data, dict):
            woulate_list.append(WoulateCreate.model_validate(data))

    #logger.debug("Woulate list: %s", woulate_list)
    results = []
    
    for woulate in woulate_list:
        logger.debug("Woulate: %s", woulate)
        # Check if full record already exists
        existing = db.query(Woulate).filter(
            Woulate.full_name == woulate.full_name,
            Woulate.assignment_date == woulate.assignment_date
            ).first()

        if existing:
            logger.debug("Woulate already existing: %s", existing)
            logger.info(f"Woulat with name '{woulate.full_name}' and with assignement date '{woulate.assignment_date}' already exists ")
            continue

        # Deactivate previous active assignments for this person only if new date is later than previous dates
        previous_assignments = db.query(Woulate).filter(
            Woulate.full_name == woulate.full_name,
            Woulate.active == True
        ).all()
        if previous_assignments:
            for previous_assignment in previous_assignments:
                if previous_assignment.assignment_date < woulate.assignment_date:
                    previous_assignment.active = False


        # Resolve jiha/wilaya to IDs using helper function
        jiha_id = None
        wilaya_id = None

        if woulate.jiha and woulate.wilaya:
            jiha_info = get_jiha_id_from_location(db, woulate.jiha)
            if jiha_info:
                # find the specific wilaya within this jiha
                wilaya_record = db.query(Jihate).filter(
                    Jihate.jiha_id == jiha_info[0],
                    Jihate.wilaya == woulate.wilaya
                ).first()

                if wilaya_record:
                    jiha_id = wilaya_record.jiha_id
                    wilaya_id = wilaya_record.wilaya_id
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Wilaya '{woulate.wilaya}' not found in jiha '{woulate.jiha}'"
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Jiha '{woulate.jiha}' not found"
                )

        # Create new record
        new_woulate = Woulate(
            full_name=woulate.full_name,
            job_description=woulate.job_description,
            job_title=extract_job_title(woulate.job_description),
            idara=woulate.idara,
            jiha_id=jiha_id,
            wilaya_id=wilaya_id,
            amala_jamaa_id=woulate.amala_jamaa_id,
            amala=woulate.amala,
            assignment_date=woulate.assignment_date,
            assignment_year=woulate.assignment_year,
            active=woulate.active
        )
    
        db.add(new_woulate)
        results.append(new_woulate)
    
    db.commit()
   
    # Refresh and format results
    response = []
    for w in results:
        db.refresh(w)
        response.append(
            WoulateSearchResult(
                id = w.id  ,
                full_name=w.full_name,
                job_title=w.job_title,
                job_description=w.job_description,
                jiha=woulate.jiha or "Unknown",
                wilaya=woulate.wilaya or "Unknown",
                amala=woulate.amala or "Unknown",
                idara=w.idara,
                active=w.active,
                assignment_date=w.assignment_date,
                assignment_year=w.assignment_year
            )
        )
    
    return response[0] if len(response) == 1 else response