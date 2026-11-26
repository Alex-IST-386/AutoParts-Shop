from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
from auth import get_current_user, get_current_admin_user, get_current_supplier_user
from schemas import SupplierOut, SupplierIn, SupplierPatch, PartOut

router = APIRouter(prefix="/suppliers", tags=["Поставщики"])

@router.get("/me", response_model=SupplierOut)
def get_my_supplier_profile(db: Session = Depends(get_db),
                            current_user: models.User = Depends(get_current_supplier_user)):
    """Профиль организации текущего поставщика."""
    supplier = db.query(models.Supplier).filter(models.Supplier.user_id == current_user.id).first()
    if not supplier:
        raise HTTPException(404, "Для этой учетной записи не создан профиль поставщика")
    return supplier


@router.get("/me/parts", response_model=List[PartOut])
def get_my_supply_status(db: Session = Depends(get_db),
                         current_user: models.User = Depends(get_current_supplier_user)):
    """Статус своих поставок: запчасти текущего поставщика с остатками на складе."""
    supplier = db.query(models.Supplier).filter(models.Supplier.user_id == current_user.id).first()
    if not supplier:
        raise HTTPException(404, "Для этой учетной записи не создан профиль поставщика")
    return db.query(models.Part).filter(models.Part.supplier_id == supplier.id).all()

@router.get("/", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_admin_user)):
    return db.query(models.Supplier).all()


@router.post("/", response_model=SupplierOut, status_code=201)
def create_supplier(data: SupplierIn,
                    db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_admin_user)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user.role != "supplier":
        raise HTTPException(400, "У пользователя должна быть роль 'supplier'")
    linked = db.query(models.Supplier).filter(models.Supplier.user_id == data.user_id).first()
    if linked:
        raise HTTPException(400, "У этого пользователя уже есть профиль поставщика")

    supplier = models.Supplier(
        name=data.name,
        contact_info=data.contact_info,
        user_id=data.user_id,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_one_supplier(supplier_id: int,
                     db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_admin_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Поставщик не найден")
    return supplier  # <-- это и был потерянный return


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, data: SupplierIn,
                    db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_admin_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user.role != "supplier":
        raise HTTPException(400, "У пользователя должна быть роль 'supplier'")
    linked = db.query(models.Supplier).filter(
        models.Supplier.user_id == data.user_id,
        models.Supplier.id != supplier_id,
    ).first()
    if linked:
        raise HTTPException(400, "У этого пользователя уже есть профиль поставщика")

    supplier.name = data.name
    supplier.contact_info = data.contact_info
    supplier.user_id = data.user_id
    db.commit()
    db.refresh(supplier)
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierOut)
def partial_update_supplier(supplier_id: int, data: SupplierPatch,
                            db: Session = Depends(get_db),
                            current_user: models.User = Depends(get_current_admin_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    update_items = data.model_dump(exclude_unset=True)

    if "user_id" in update_items:
        user = db.query(models.User).filter(models.User.id == update_items["user_id"]).first()
        if not user:
            raise HTTPException(404, "Пользователь не найден")
        if user.role != "supplier":
            raise HTTPException(400, "У пользователя должна быть роль 'supplier'")
        linked = db.query(models.Supplier).filter(
            models.Supplier.user_id == update_items["user_id"],
            models.Supplier.id != supplier_id,
        ).first()
        if linked:
            raise HTTPException(400, "У этого пользователя уже есть профиль поставщика")

    for key, value in update_items.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int,
                    db: Session = Depends(get_db),
                    current_user: models.User = Depends(get_current_admin_user)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Поставщик не найден")

    db.delete(supplier)
    db.commit()
    return {"Уведомление": "Поставщик удален"}
