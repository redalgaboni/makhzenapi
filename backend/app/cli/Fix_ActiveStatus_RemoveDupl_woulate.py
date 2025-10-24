from backend.app.db.session import SessionLocal
from backend.app.db.models import Woulate

db = SessionLocal()

# Get all woulate records
woulate_records = db.query(Woulate).all()

# Remove duplicates
print("Removing duplicates and keeping the first one...")

woulate_records = db.query(Woulate).all()

for woulate in woulate_records:
    matching_records = db.query(Woulate).filter(
        Woulate.full_name == woulate.full_name,
        Woulate.jiha_id == woulate.jiha_id,
        Woulate.wilaya_id == woulate.wilaya_id,
        Woulate.amala_jamaa_id == woulate.amala_jamaa_id
    ).all()

    if len(matching_records) > 1:
        print(f"Removing duplicate woulate_id: {woulate.id}")
        for record in matching_records[1:]:
            db.delete(record)

db.commit()

# Fix active status for a full_name with different jiha/wilaya/amala
print("Fixing active status for a woulate with different jiha/wilaya/amala...")

for woulate in woulate_records:
    matching_records = db.query(Woulate).filter(
        Woulate.full_name == woulate.full_name,
        Woulate.jiha_id == woulate.jiha_id,
        Woulate.wilaya_id == woulate.wilaya_id,
        Woulate.amala_jamaa_id == woulate.amala_jamaa_id
    ).all()

    if len(matching_records) > 1:
        latest_record = max(matching_records, key=lambda x: x.assignment_date)
        for record in matching_records:
            if record.id != latest_record.id:
                print(f"Setting active to False for woulate_id: {record.id}")
                record.active = False
        

db.commit()

# Fix active status for same jiha/wilaya/amala with different woulate names
print("Fixing active status for same jiha/wilaya/amala with different woulate names...")

for woulate in woulate_records:
    matching_records = db.query(Woulate).filter(
        Woulate.jiha_id == woulate.jiha_id,
        Woulate.wilaya_id == woulate.wilaya_id,
        Woulate.amala_jamaa_id == woulate.amala_jamaa_id
    ).all()

    if len(matching_records) > 1:
        latest_record = max(matching_records, key=lambda x: x.assignment_date)
        for record in matching_records:
            if record.assignment_date < latest_record.assignment_date:
                print(f"Setting active to False for woulate_id: {record.id}")
                record.active = False
            #else:
            #    print(f"Setting active to True for woulate_id: {record.id}")
            #    record.active = True

db.commit()
db.close()

print("Done")
