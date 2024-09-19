from sqlalchemy.orm import Session
from .import models,schemas
from datetime import datetime, timedelta
from fastapi import HTTPException

# 予約取得（全てのリソース）
# def get_reservation(db: Session,skip:int =0, limit: int =100):
#     return db.query(models.Reservation).offset(skip).limit(limit).all()

# 予約取得(リソースごと)
def get_reservations_by_resource(db: Session, resource_id: int,skip:int =0, limit: int =100):
    return db.query(models.Reservation).filter(models.Reservation.resourceId == resource_id).all()


# 予約登録
# 引数はfastAPI側のデータ型で受け取る。DBに保存するときは、DBの型で保存する
def create_reservation(db: Session,reservation:schemas.Reservation):
    
    print(f"Creating reservation: {reservation}")  # デバッグプリント
    
    #重複チェック
    overlapping_reservations = db.query(models.Reservation).filter(
        models.Reservation.resourceId == reservation.resourceId,
        models.Reservation.startTime < reservation.endTime,
        models.Reservation.endTime > reservation.startTime
    ).all()
    
    if overlapping_reservations:
        raise HTTPException(status_code=400, detail='予約が重複しています。別の時間を選択してください')
    
    db_reservation = models.Reservation(
        userName = reservation.userName,
        startTime =reservation.startTime,
        endTime = reservation.endTime,
        resourceId = reservation.resourceId
        )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    print(f"Created reservation: {db_reservation}")  # デバッグプリント
    return db_reservation

# 予約削除
def delete_reservation(db: Session,reservation_id:int):
    db_reservation = db.query(models.Reservation).filter(models.Reservation.userId ==reservation_id).first()
    print(f"reservationId:{db_reservation}")
    if db_reservation:
        db.delete(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        print(f"delete reservation: {db_reservation}")  # デバッグプリント
        return db_reservation
    else:
        print(f"Reservation_idがみつかりません")
        return
    
# 古い予約を削除
def delete_old_reservations(db: Session):
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    db_reservations = db.query(models.Reservation).filter(models.Reservation.endTime < one_week_ago).all()
    for reservation in db_reservations:
        db.delete(reservation)
    db.commit()
    print(f"Deleted reservations older than {one_week_ago}")
    
    
# リソース取得
def get_resources(db: Session,skip:int =0,limit:int =100):
    return db.query(models.Resources).offset(skip).limit(limit).all()


#リソースIdからリソースデータを取得
def get_resource(db: Session, resource_id:int):
    return db.query(models.Resources).filter(models.Resources.resourceId == resource_id).first()


# リソース登録
def create_resource(db: Session,resource:schemas.ResourceCreate):
    db_resource = models.Resources(resourceName=resource.resourceName)
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


# リソース削除
def delete_resource(db: Session,resource_id:int):
    db_resource = db.query(models.Resources).filter(models.Resources.resourceId ==resource_id).first()
    print(f"resourceId:{db_resource}")
    if db_resource:
        db.delete(db_resource)
        db.commit()
        db.refresh(db_resource)
        print(f"delete resource: {db_resource}")
        return db_resource
    else:
        print(f"Resource_idがみつかりません")
        return

# 予約削除
def delete_reservation(db: Session,reservation_id:int):
    db_reservation = db.query(models.Reservation).filter(models.Reservation.userId ==reservation_id).first()
    print(f"reservationId:{db_reservation}")
    if db_reservation:
        db.delete(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        print(f"delete reservation: {db_reservation}")  # デバッグプリント
        return db_reservation
    else:
        print(f"Reservation_idがみつかりません")
        return
    

# リソース名の変更
def update_resource(db: Session, resource_id:int, resource_update:schemas.ResourceUpdate):
    db_resource = db.query(models.Resources).filter(models.Resources.resourceId == resource_id).first()
    if db_resource:
        db_resource.resourceName = resource_update.resourceName
        db.commit()
        db.refresh(db_resource)
        return db_resource
    return None