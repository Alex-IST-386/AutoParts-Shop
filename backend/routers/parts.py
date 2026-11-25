from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_current_user
from typing import List
from schemas import PartOut, PartIn, PartPatch, PartModelOut, PartModelIn, PartModelPatch
from collections import deque

router = APIRouter(prefix = "/parts", tags = ["Запчасти"])

@router.get("/", response_model = List[PartOut])
def list_parts(db: Session = Depends(get_db)):
    part = db.query(models.Part).all()

    return part

@router.post("/", response_model = PartOut)
def create_part(data: PartIn, db:  Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role not in ["admin", "seller"]:
        raise HTTPException(403, "Только администратор или продавец может добавлять запчасти")

    part = models.Part(
        article = data.article,
        name = data.name,
        price = data.price,
        stock_quantity = data.stock_quantity,
        supplier_id = data.supplier_id
    )

    db.add(part)
    db.commit()
    db.refresh(part)

    return part

@router.get("/{part_id}", response_model = PartOut)
def get_one_part(part_id: int, db: Session = Depends(get_db)):
    part = db.query(models.Part).filter(models.Part.id == part_id).first()

    if not part:
        raise HTTPException(404, "Запчасть не найдена")
    return part

@router.put("/{part_id}", response_model = PartOut)
def update_part(part_id: int, data: PartIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может изменять запчасти")

    part = db.query(models.Part).filter(models.Part.id == part_id).first()

    part.article = data.article
    part.name = data.name
    part.price = data.price
    part.stock_quantity = data.stock_quantity

    db.commit()
    db.refresh(part)

    return part

@router.patch("/{part_id}", response_model = PartOut)
def partial_update_part(part_id: int, data: PartPatch, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может изменять изменять запчасти")

    part = db.query(models.Part).filter(models.Part.id == part_id).first()

    if not part:
        raise HTTPException(404, "Запчасть не найдена")

    update_items = data.model_dump(exclude_unset = True)

    for key, value in update_items.items():
        setattr(part, key, value)

    db.commit()
    db.refresh(part)

    return part

@router.delete("/{part_id}", response_model = PartOut)
def delete_part(part_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может удалять запчасти")

    part = db.query(models.Part).filter(models.Part.id == part_id).first()

    if not part:
        raise HTTPException(404, "Запчасть не найдена")

    db.delete(part)
    db.commit()

    return {"Уведомление": "Запчасть удалена"}

@router.get("/compatibility/", response_model = List[PartModelOut])
def list_part_models(db: Session = Depends(get_db)):
    return db.query(models.PartModel).all()

@router.post("/compatibility/", response_model = PartModelOut)
def create_part_model(data: PartModelIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Только админ")

    part_model = models.PartModel(**data.model_dump())

    db.add(part_model)
    db.commit()
    db.refresh(part_model)

    return part_model


@router.get("/{part_id}/analogs", response_model=List[PartOut])
def get_analogs(part_id: int, db: Session = Depends(get_db)):
    part = db.query(models.Part).filter(models.Part.id == part_id).first()
    if not part:
        raise HTTPException(404, "Запчасть не найдена")

    queue = deque([(part_id, 0)])
    visited = set([part_id])
    found_analogs = []
    max_depth = 2  # Ищем аналоги на глубину до 2 уровней

    while queue:
        current_id, depth = queue.popleft()
        if depth >= max_depth:
            continue

        links = db.query(models.Analog).filter(models.Analog.part_id == current_id).all()
        for link in links:
            analog_id = link.analog_part_id
            if analog_id not in visited:
                visited.add(analog_id)
                analog_part = db.query(models.Part).filter(models.Part.id == analog_id).first()
                if analog_part:
                    found_analogs.append(analog_part)
                    queue.append((analog_id, depth + 1))

    return found_analogs