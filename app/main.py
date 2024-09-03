from fastapi import FastAPI,Depends,WebSocket,WebSocketDisconnect,HTTPException
from sqlalchemy.orm import Session
from . import crud,models,schemas
from .database import SessionLocal,engine
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import logging
from apscheduler.schedulers.background import BackgroundScheduler

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
    "http://127.0.0.1:8000",
    "http://10.111.170.194:8800"
    # 追加で許可したいオリジンがあればここに追加
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients=[]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/reservations",response_model=List[schemas.Reservation])
async def read_reservation(db:Session=Depends(get_db),skip:int =0,limit: int =100):
    reservations = crud.get_reservation(db,skip=skip,limit=limit)
    return reservations

@app.post("/reservations",response_model=schemas.Reservation)
async def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    new_reservation = crud.create_reservation(db=db,reservation=reservation)
    await manager.broadcast("New reservation added")
    return new_reservation

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

