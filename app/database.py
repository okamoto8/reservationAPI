from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import models

# データベースURLの設定
DATABASE_URL = "postgresql://postgres:mahhy0801@localhost/reservation"

# SQLAlchemyエンジンの作成
engine = create_engine(DATABASE_URL)
# セッションの作成
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)


# ベースクラスの宣言
Base = declarative_base()


# テーブルがない場合は作成する
Base.metadata.create_all(bind=engine)