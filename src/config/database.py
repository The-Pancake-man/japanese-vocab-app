from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# 讀取資料庫連線字串，也就是 DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://vocab_user:vocab_pass@localhost:5432/vocab_db"
)

# 建立 engine
# SQLAlchemy 和 database 溝通的核心物件
engine = create_engine(DATABASE_URL)

# 建立 SessionLocal
# 用來產生 database session 的工廠
# 之後每次 API 要CRUD，都會需要一個 db session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 建立 Base
# 這個 Python class 會被 SQLAlchemy 對應成 database table
Base = declarative_base()

# 建立 get_db()
# 每次 API request 進來時，FastAPI 幫你開一個 DB session，API 結束後自動關掉
# 這樣就不用你每個 route 手動開關 database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()