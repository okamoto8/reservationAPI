from fastapi import FastAPI,Depends,WebSocket,WebSocketDisconnect,HTTPException
from sqlalchemy.orm import Session
from . import crud,models,schemas
from .database import SessionLocal,engine
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import JSONResponse



models.Base.metadata.create_all(bind = engine)
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError as e:
                logging.error(f"WebSocket error:{e}")
                self.active_connections.remove(connection)


manager = ConnectionManager()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.111.170.194:8800"
    # 追加で許可したいオリジンがあればここに追加
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # allow_websockets=True,
)

connected_clients=[]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/reservations/{resource_id}",response_model=List[schemas.Reservation])
async def read_reservation(resource_id: int, db:Session=Depends(get_db),skip:int =0,limit: int =100):
    reservations = crud.get_reservations_by_resource(db,skip=skip,limit=limit,resource_id=resource_id)
    return reservations

#DB設計変更前のメソッド
# @app.get("/reservations",response_model=List[schemas.Reservation])
# async def read_reservation(db:Session=Depends(get_db),skip:int =0,limit: int =100):
#     reservations = crud.get_reservation(db,skip=skip,limit=limit)
#     return reservations

@app.post("/reservations",response_model=schemas.Reservation)
async def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    try:
        new_reservation = crud.create_reservation(db=db,reservation=reservation)
        await manager.broadcast("New reservation added")
        return new_reservation
    except HTTPException as e:
        return JSONResponse(status_code = e.status_code, content={"error":e.detail})
        

@app.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    try:
        reservation = db.query(models.Reservation).filter(models.Reservation.userId == reservation_id).first()
        if reservation is None:
            raise HTTPException(status_code=404, detail="Reservation not found")
        
        db.delete(reservation)
        db.commit()
        

        await manager.broadcast(f"Reservation with ID {reservation_id}has been deleted")

        return {"message": "Reservation deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting reservation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 過去のデータを削除する
scheduler = BackgroundScheduler()

def scheduled_delete_old_reservations():
    db = SessionLocal()
    crud.delete_old_reservations(db)
    db.close()

# 定期的なジョブの設定（毎日正午に実行）
scheduler.add_job(scheduled_delete_old_reservations, 'cron', hour=12)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message :{data}")
    except WebSocketDisconnect as e:
        logging.error(f"WebSocket disconnected with code {e.code}and reason:{e.reason}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

#リソースの取得（例：会議室A,B,C 貸し出し表：A,B,C）
@app.get("/resources",response_model=List[schemas.Resource])
async def read_resources(db:Session = Depends(get_db),skip:int =0,limit:int =100):
    resources = crud.get_resources(db,skip=skip,limit=limit)
    return resources

#リソース単体の情報を取得
@app.get("/resources/{resource_id}",response_model=schemas.Resource)
async def read_resource(resource_id:int, db:Session = Depends(get_db)):
    resource = crud.get_resource(db,resource_id)
    return resource

#リソースの登録
@app.post("/resources",response_model=schemas.Resource)
async def create_resource(resource:schemas.ResourceCreate,db: Session = Depends(get_db)):
    return crud.create_resource(db=db,resource=resource)


#リソースの削除
@app.delete("/resources/{resource_id}")
async def delete_resource(resource_id: int,db: Session = Depends(get_db)):
    try:
        resource = db.query(models.Resources).filter(models.Resources.resourceId == resource_id).first()
        if resource is None:
            raise HTTPException(status_code=404,detail="Resource not found")
        
        db.delete(resource)
        db.commit()
    except Exception as e:
        logging.error(f"Error deleting resource:{e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#リソースの名前の更新
@app.put("/resources/{resource_id}",response_model=schemas.ResourceUpdate)
async def update_resource(resource_id : int, resource_update:schemas.ResourceUpdate, db:Session =Depends(get_db)):
    try:
        updated_resource = crud.update_resource(db,resource_id,resource_update)
        if updated_resource is None:
            raise HTTPException(status_code=404,detail="Resource not found")
        return updated_resource
    except Exception as e:
        logging.error(f"Error updating resource:{e}")
        raise HTTPException(status_code=500,detail="Internal Server Error")