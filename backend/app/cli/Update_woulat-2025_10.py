from backend.app.db.session import SessionLocal
from backend.app.db.models import Woulate, Jihate
from backend.helper_functions import get_jiha_id_from_location, extract_job_title, \
    get_amala_id_from_name

AssignmentDate="2025-10-19"
AssignmentYear=2025

# data: (full_name, job_description, jiha, wilaya, amala)
ASSIGNMENTS = [
    ("خطيب الهبيل", "والي جهة مراكش-آسفي وعامل عمالة مراكش", "جهة مراكش آسفي", "عمالة مراكش", None),
    ("خالد آيت طالب", "والي جهة فاس-مكناس وعامل عمالة فاس", "جهة فاس مكناس", "عمالة فاس",None),
    ("امحمد عطفاوي", "والي جهة الشرق وعامل عمالة وجدة-أنجاد", "جهة الشرق", "عمالة وجدة أنكاد",None),
    ("فؤاد حاجي", "عامل إقليم الحسيمة", "جهة طنجة تطوان الحسيمة", "إقليم الحسيمة",None),
    ("حسن زيتوني", "عامل إقليم أزيلال", "جهة بني ملال خنيفرة", "إقليم أزيلال",None),
    ("سيدي الصالح داحا", "عامل إقليم الجديدة", "جهة الدار البيضاء سطات", "إقليم الجديدة",None),
    ("عبد الخالق مرزوقي", "عامل عمالة مقاطعات الدارالبيضاء-انفا", "جهة الدار البيضاء سطات","عمالة الدار البيضاء" ,"عمالة مقاطعات الدارالبيضاء-انفا"),
    ("محمد علمي ودان", "عامل إقليم زاكورة", "جهة درعة تافيلالت", "إقليم زاكورة",None),
    ("مصطفى المعزة", "عامل إقليم الحوز", "جهة مراكش آسفي", "إقليم الحوز",None),
    ("رشيد بنشيخي", "عامل إقليم تازة", "جهة فاس مكناس", "إقليم تازة",None),
    ("محمد الزهر", "عامل عمالة إنزكان-آيت ملول", "جهة سوس ماسة", "عمالة إنزكان أيت ملول",None),
    ("محمد خلفاوي", "عامل إقليم الفحص-أنجرة", "جهة طنجة تطوان الحسيمة", "إقليم الفحص أنجرة",None),
    ("زكرياء حشلاف", "عامل إقليم شفشاون", "جهة طنجة تطوان الحسيمة", "إقليم شفشاون",None),
    ("عبد العزيز زروالي", "عامل إقليم سيدي قاسم", "جهة الرباط سلا القنيطرة", "إقليم سيدي قاسم",None),
    ("عبد الكريم الغنامي", "عامل إقليم تاونات", "جهة فاس مكناس", "إقليم تاونات",None),
]

def update_assignements():
    db = SessionLocal()

    for full_name, job_description, jiha, wilaya, amala in ASSIGNMENTS:
        print(f"Processing: {full_name}")
        # Resolve jiha/wilaya to IDs
        jiha_info = get_jiha_id_from_location(db, jiha)
        if not jiha_info:
            print(f"Jiha '{jiha}' not found for {full_name}")
            continue
            
        jiha_id, jiha_name = jiha_info
        
        wilaya_record = db.query(Jihate).filter(
            Jihate.jiha_id == jiha_id,
            Jihate.wilaya == wilaya
        ).first()

        if not wilaya_record:
            print(f"Wilaya '{wilaya}' not found in jiha '{jiha}' for {full_name}")
            continue

        # Resolve amala to ID
        if amala:
            amala_id = get_amala_id_from_name(db, amala)
            #print(f"Amala ID: {amala_id}")
            if not amala_id:
                print(f"Amala '{amala}' not found for {full_name}")
                continue
        else:
            amala_id = None
            
        # Deactivate previous assignments such as
        if amala:
            db.query(Woulate).filter(
                Woulate.jiha_id == jiha_id,
                Woulate.wilaya_id == wilaya_record.wilaya_id,
                Woulate.amala_jamaa_id == amala_id,
                Woulate.assignment_date < AssignmentDate,
                Woulate.active == True
            ).update({"active": False})
        else:
            db.query(Woulate).filter(
                Woulate.jiha_id == jiha_id,
                Woulate.wilaya_id == wilaya_record.wilaya_id,
                Woulate.assignment_date < AssignmentDate,
                Woulate.active == True
            ).update({"active": False})
    
        
        # Create new assignment
        new_woulate = Woulate(
            full_name=full_name,
            job_description=job_description,
            job_title=extract_job_title(job_description),
            idara="ترابية",
            jiha_id=wilaya_record.jiha_id,
            wilaya_id=wilaya_record.wilaya_id,
            assignment_date=AssignmentDate,
            assignment_year=AssignmentYear,
            amala=amala if amala else None,
            amala_jamaa_id=amala_id if amala_id else None,
            active=True
        )
        db.add(new_woulate)
    
    db.commit()
    print("All assignements updated successfully!")
    
    db.close()

if __name__ == "__main__":
    update_assignements()