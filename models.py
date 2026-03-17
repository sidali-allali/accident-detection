from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, Field
from typing import Optional
from database import Base

# نموذج قاعدة البيانات
class Accident(Base):
    __tablename__ = "accidents"

    id = Column(Integer, primary_key=True, index=True)
    nbr_of_cars = Column(Integer, nullable=False)
    time = Column(String, nullable=False)
    damage = Column(String, nullable=False)
    video_path = Column(String, nullable=True)  # اسم الملف فقط

# نموذج Pydantic للإدخال
class AccidentCreate(BaseModel):
    nbr_of_cars: int = Field(..., gt=0, description="عدد الحوادث")
    time: str = Field(..., description="وقت الحادث")
    damage: str = Field(..., description="نوع الضرر")

# نموذج Pydantic للاستجابة
class AccidentResponse(BaseModel):
    id: int
    nbr_of_cars: int
    time: str
    damage: str
    video_url: Optional[str] = None

    class Config:
        from_attributes = True # 👈 تم تغيير orm_mode إلى from_attributes