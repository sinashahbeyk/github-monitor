from sqlalchemy import Column, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./github_repos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(String, index=True)
    name = Column(String)
    full_name = Column(String, primary_key=True, index=True)
    url = Column(String)
    description = Column(String)
    language = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    keyword = Column(String)


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "url": self.url,
            "description": self.description,
            "language": self.language,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "keyword": self.keyword
        }