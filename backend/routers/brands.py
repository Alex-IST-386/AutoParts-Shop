from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from typing import List

from auth import get_current_user
from schemas import BrandOut, BrandIn, BrandPatch
import models

router = APIRouter(prefix = "/brands", tags = ["Марки"])

@router.get("/", response_model = List[BrandOut])
def list_of_brands(db: Session = Depends(get_db)):
    brand = db.query(models.Brand).all()

    return brand

@router.post("/", response_model = BrandOut)
def create_brand(data: BrandIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может добавлять марки")

    brand = models.Brand(
        name = data.name
    )

    db.add(brand)
    db.commit()
    db.refresh(brand)

    return brand

@router.get("/{brand_id}", response_model = BrandOut)
def get_one_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(404, "Марка авто не найдена")

    return brand

@router.put("/{brand_id}", response_model = BrandOut)
def update_brand(brand_id: int, data: BrandIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может изменять марки")

    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(404, "Марка авто не найдена")

    brand.name = data.name

    db.commit()
    db.refresh(brand)

    return brand

@router.patch("/{brand_id}", response_model = BrandOut)
def partial_update_brand(brand_id: int, data: BrandPatch, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может изменять марки")

    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(404, "Марка авто не найдена")

    update_items = data.model_dump(exclude_unset = True)

    for key, value in update_items.items():
        setattr(brand, key, value)

    db.commit()
    db.refresh(brand)

    return brand

@router.delete("/{brand_id}", response_model = BrandOut)
def delete_brand(brand_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может удалять марки")

    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(404, "Марка авто не найдена")

    db.delete(brand)
    db.commit()

    return {"Уведомление": "Марка авто удалена"}
