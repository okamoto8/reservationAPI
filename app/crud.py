from sqlalchemy.orm import Session
from .import models,schemas
from datetime import datetime, timedelta
from fastapi import HTTPException

# 予約一覧
def get_reservation(db: Session,skip:int =0, limit: int =100):
    return db.query(models.Reservation).offset(skip).limit(limit).all()

# 予約登録
# 引数はfastAPI側のデータ型で受け取る。DBに保存するときは、DBの型で保存する
def create_reservation(db: Session,reservation:schemas.Reservation):
    
    print(f"Creating reservation: {reservation}")  # デバッグプリント
    
    #重複チェック
    overlapping_reservations = db.query(models.Reservation).filter(
        models.Reservation.startTime < reservation.endTime,
        models.Reservation.endTime > reservation.startTime
    ).all()
    
    if overlapping_reservations:
        raise HTTPException(status_code=400, detail='予約が重複しています。別の時間を選択してください')
    
    db_reservation = models.Reservation(
        userName = reservation.userName,
        startTime =reservation.startTime,
        endTime = reservation.endTime,
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