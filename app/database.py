from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


# .env ファイルから環境変数を読み込む
load_dotenv()

# データベースURLの設定
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemyエンジンの作成
engine = create_engine(DATABASE_URL)
# セッションの作成
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)


# ベースクラスの宣言
Base = declarative_base()


# テーブルがない場合は作成する
Base.metadata.create_all(bind=engine)