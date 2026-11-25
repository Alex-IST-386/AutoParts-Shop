from fastapi import FastAPI, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from schemas import CarModelIn, CarModelOut, CarModelPatch
import models
from auth import get_current_user
router = APIRouter(prefix = "/models", tags = ["Модели Авто"])

@router.get("/", response_model = List[CarModelOut])
def models_list(db: Session = Depends(get_db)):
    model = db.query(models.CarModel).all()

    return model

@router.post("/", response_model = CarModelOut)
def create_model(data: CarModelIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может добавлять модели авто")

    model = models.CarModel(
        name = data.name,
        brand_id = data.brand_id
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return model

@router.get("/{model_id}", response_model = CarModelOut)
def get_one_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(models.CarModel).filter(models.CarModel.id == model_id).first()

    if not model:
        return HTTPException(404, "Модель авто не найдена")

    return model

@router.put("/{model_id}", response_model = CarModelOut)
def update_model(model_id: int, data: CarModelIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может изменять модели авто")

    model = db.query(models.CarModel).filter(models.CarModel.id == model_id).first()

    if not model:
        return HTTPException(404, "Модель авто не найдена")

    model.name = data.name
    model.brand_id = data.brand_id

    db.commit()
    db.refresh(model)

    return model

@router.patch("/{model_id}", response_model = CarModelOut)
def partial_update_model(model_id: int, data: CarModelPatch, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может изменять модели авто")

    model = db.query(models.CarModel).filter(models.CarModel.id == model_id).first()

    if not model:
        return HTTPException(404, "Модель авто не найдена")

    update_items = data.model_dump(exclude_unset = True)

    for key, value in update_items.items():
        setattr(model, key, value)

    db.commit()
    db.refresh(model)

    return model

@router.delete("/{model_id}", response_model = CarModelOut)
def delete_model(model_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может удалять модели")

    model = db.query(models.CarModel).filter(models.CarModel.id == model_id).first()

    if not model:
        raise HTTPException(404, "Модель авто не найдена")

    db.delete(model)
    db.commit()

    return {"Уведомление": "Модель авто удалена"}
