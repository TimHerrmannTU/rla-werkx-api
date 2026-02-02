# crud/log.py
from sqlalchemy.orm import Session
from models.log import LogDailySummary, LogProjectHour, LogTimeframe
from schemas.log import DailyLogSync

def sync_daily_log(db: Session, schema: DailyLogSync):
    # 1. Fetch or Create Parent
    db_obj = db.query(LogDailySummary).filter(
        LogDailySummary.date == schema.date,
        LogDailySummary.employee_id == schema.employee_id
    ).first()

    if not db_obj:
        db_obj = LogDailySummary(
            date=schema.date,
            employee_id=schema.employee_id,
            target_hours=schema.target_hours
        )
        db.add(db_obj)
        db.flush() # Get ID for children

    # 2. Update Parent Fields
    db_obj.status = schema.status
    db_obj.status_target_factor = schema.status_target_factor
    db_obj.status_note = schema.status_note
    db_obj.general_note = schema.general_note
    db_obj.target_hours = schema.target_hours

    # 3. Sync Project Hours (Reconciliation)
    _sync_children(
        db, 
        owner_id=db_obj.id,
        model_class=LogProjectHour,
        incoming_data=schema.project_hours,
        existing_items=db_obj.project_hours
    )

    # 4. Sync Timeframes
    _sync_children(
        db,
        owner_id=db_obj.id,
        model_class=LogTimeframe,
        incoming_data=schema.timeframes,
        existing_items=db_obj.timeframes
    )

    db.commit()
    db.refresh(db_obj)
    return db_obj

def _sync_children(db: Session, owner_id: int, model_class, incoming_data, existing_items):
    """Generic reconciliation: Update, Create, or Delete orphans."""
    incoming_ids = {item.id for item in incoming_data if item.id is not None}
    
    # DELETE orphans (exists in DB but not in request)
    for existing in existing_items:
        if existing.id not in incoming_ids:
            db.delete(existing)

    # CREATE or UPDATE
    for incoming in incoming_data:
        data = incoming.model_dump()
        if incoming.id: # UPDATE
            db_item = db.query(model_class).filter(model_class.id == incoming.id).first()
            if db_item:
                for key, value in data.items():
                    setattr(db_item, key, value)
        else: # CREATE
            data.pop("id", None)
            new_item = model_class(**data, daily_entry_id=owner_id)
            db.add(new_item)