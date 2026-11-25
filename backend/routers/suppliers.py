from fastapi import FastAPI, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from typing import List
import models

from auth import get_current_user
from schemas import SupplierOut, SupplierIn, SupplierPatch

router = APIRouter(prefix = "/suppliers", tags = ["Поставщики"])

@router.get("/", response_model = List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    supplier = db.query(models.Supplier).all()

    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(403, "Список поставщиков недоступен")

    return supplier

@router.post("/", response_model = SupplierOut)
def create_supplier(data: SupplierIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    if current_user.role not in ["admin", "supplier", "manager"]:
        raise HTTPException(403, "Вы не поставщик/администратор")

    supplier = models.Supplier(
        name = data.name,
        contact_info = data.contact_info,
        user_id = current_user.id
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    return supplier

@router.get("/{supplier_id}", response_model = SupplierOut)
def get_one_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()

    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    if current_user.role != "admin":
        raise HTTPException(403, "Просмотр поставщиков доступен только администраторам")

@router.put("/{supplier_id}", response_model = SupplierOut)
def update_supplier(supplier_id: int, data: SupplierIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()

    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    if current_user.role != "supplier":
        raise HTTPException(403, "Вы не поставщик")

    if supplier.user_id != current_user.id:
        raise HTTPException(403, "Вы не можете изменить данные о поставщике")


    supplier.name = data.name
    supplier.contact_info = data.contact_info

    db.commit()
    db.refresh(supplier)

    return supplier

@router.patch("/{supplier_id}", response_model = SupplierOut)
def partial_update_supplier(supplier_id: int, data: SupplierPatch, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()

    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    if current_user.role != "supplier":
        raise HTTPException(403, "Вы не поставщик")

    if supplier.id != current_user.id:
        raise HTTPException(403, "Вы не можете изменить поставщика")

    update_items = data.model_dump(exclude_unset = True)

    for key, value in update_items.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)

    return supplier

@router.delete("/{supplier_id}", response_model = SupplierOut)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()

    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(403, "Вы не можете удалить поставщика")

    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    db.delete(supplier)
    db.commit()

    return {"Уведомление": "Поставщик удален"}