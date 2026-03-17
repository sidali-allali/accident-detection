from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware  # 👈 الإضافة الجديدة
import os
import uuid
from typing import List

from database import engine, get_db, Base
from models import Accident, AccidentResponse
from sqlalchemy.orm import Session

# إنشاء الجداول في قاعدة البيانات
# ==============================
Base.metadata.create_all(bind=engine)

# إعدادات التطبيق
# ==============================
app = FastAPI(
    title="Accident Detection API",
    description="Backend for Traffic Accident Detection and Dashboard",
)

# إعدادات الـ CORS (السماح بالاتصال من الـ Dashboard)
# ==================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح بالوصول من أي رابط. في الإنتاج استبدل "*" برابط الـ Dashboard
    allow_credentials=True,
    allow_methods=["*"],  # يسمح بجميع العمليات (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # يسمح بجميع الـ Headers
)

# إعدادات الأمان والرفع
# ==============================
VIDEO_DIR = "videos"
ALLOWED_TYPES = ["video/mp4", "video/x-msvideo", "video/quicktime"]
ALLOWED_EXTENSIONS = [".mp4", ".avi", ".mov"]
MAX_SIZE = 100 * 1024 * 1024  # 100MB
CHUNK_SIZE = 1024 * 1024      # 1MB لكل جزء

# إنشاء مجلد الفيديوهات إذا لم يكن موجوداً
os.makedirs(VIDEO_DIR, exist_ok=True)

# نقطة النهاية الرئيسية
# ==============================
@app.get("/")
def root():
    return {
        "message": "Backend is running and CORS is enabled",
        }

# إنشاء حادث جديد مع فيديو
# ==============================
@app.post("/accidents", response_model=AccidentResponse)
async def create_accident(
    nbr_of_cars: int = Form(..., gt=0, description="Number of cars in the accident"),
    time: str = Form(..., description="Time of accident"),
    damage: str = Form(..., description="Description of damage"),
    video: UploadFile = File(..., description="Accident video file")
):
    # 1. التحقق من نوع الملف والامتداد
    if video.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="نوع الملف غير مدعوم")
    
    ext = os.path.splitext(video.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="امتداد الملف غير مسموح")
    
    # 2. إنشاء اسم فريد وحفظ الملف
    video_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(VIDEO_DIR, video_filename)
    
    total_size = 0
    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await video.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_SIZE:
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail="الملف كبير جداً (الحد الأقصى 100MB)")
                buffer.write(chunk)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"خطأ في الرفع: {str(e)}")
    
    # 3. الحفظ في قاعدة البيانات
    with get_db() as db:
        accident = Accident(
            nbr_of_cars=nbr_of_cars,
            time=time,
            damage=damage,
            video_path=video_filename
        )
        db.add(accident)
        db.commit()
        db.refresh(accident)
    
    return {
        "id": accident.id,
        "nbr_of_cars": accident.nbr_of_cars,
        "time": accident.time,
        "damage": accident.damage,
        "video_url": f"/videos/{accident.id}"
    }

# عرض فيديو حادث معين
# ==============================
@app.get("/videos/{accident_id}")
def get_video(accident_id: int):
    with get_db() as db:
        accident = db.query(Accident).filter(Accident.id == accident_id).first()
    
    if not accident or not accident.video_path:
        raise HTTPException(status_code=404, detail="الفيديو غير موجود")
    
    full_path = os.path.join(VIDEO_DIR, accident.video_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="ملف الفيديو مفقود من السيرفر")
    
    return FileResponse(full_path, media_type="video/mp4")

# عرض جميع الحوادث (للداتشبورد)
# ==============================
@app.get("/accidents", response_model=List[AccidentResponse])
def get_all_accidents():
    with get_db() as db:
        accidents = db.query(Accident).all()
    
    result = []
    for acc in accidents:
        result.append({
            "id": acc.id,
            "nbr_of_cars": acc.nbr_of_cars,
            "time": acc.time,
            "damage": acc.damage,
            "video_url": f"/videos/{acc.id}" if acc.video_path else None
        })
    return result

# حذف حادث
# ==============================
@app.delete("/accidents/{accident_id}")
def delete_accident(accident_id: int):
    with get_db() as db:
        accident = db.query(Accident).filter(Accident.id == accident_id).first()
        if not accident:
            raise HTTPException(status_code=404, detail="الحادث غير موجود")
        
        if accident.video_path:
            v_path = os.path.join(VIDEO_DIR, accident.video_path)
            if os.path.exists(v_path):
                os.remove(v_path)
        
        db.delete(accident)
        db.commit()
    return {"message": "Deleted successfully"}

# تشغيل السيرفر
# ==============================
if __name__ == "__main__":
    import uvicorn
    # نمرر اسم الملف "main" ونقطة ثم اسم التطبيق "app" داخل نص
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)