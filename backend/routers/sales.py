from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
from typing import List
from schemas import SaleOut, SaleIn, SaleItemOut, SaleItemIn

router = APIRouter(prefix="/sales", tags=["Продажи"])


# --- ЧЕКИ ---
@router.get("/", response_model=List[SaleOut])
def list_sales(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "admin":
        return db.query(models.Sale).all()
    elif current_user.role == "seller":
        # Продавец видит только СВОИ чеки
        return db.query(models.Sale).filter(models.Sale.seller_id == current_user.id).all()
    else:
        raise HTTPException(403, "Нет доступа к истории продаж")


@router.post("/", response_model=SaleOut)
def create_sale(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "seller":
        raise HTTPException(403, "Только продавец создает чеки")

    # Создаем пустой чек (сумма пока 0)
    sale = models.Sale(total_price=0, seller_id=current_user.id)
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/{sale_id}", response_model=SaleOut)
def get_one_sale(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(404, "Продажа не найдена")
    if current_user.role == "seller" and sale.seller_id != current_user.id:
        raise HTTPException(403, "Вы можете смотреть только свои чеки")
    return sale


@router.delete("/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор может аннулировать чек")
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(404, "Продажа не найдена")
    db.delete(sale)
    db.commit()
    return {"message": "Чек аннулирован"}


# --- ПОЗИЦИИ ЧЕКА ---
# Используем путь /items/ чтобы не было конфликта с /{sale_id}
@router.get("/items/", response_model=List[SaleItemOut])
def list_sale_items(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Только администратор видит все позиции")
    return db.query(models.SaleItem).all()


@router.post("/items/", response_model=SaleItemOut)
def create_sale_item(data: SaleItemIn, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    if current_user.role != "seller":
        raise HTTPException(403, "Только продавец может добавлять товары в чек")

    # 1. Проверяем, есть ли товар на складе
    part = db.query(models.Part).filter(models.Part.id == data.part_id).first()
    if not part:
        raise HTTPException(404, "Запчасть не найдена")
    if part.stock_quantity < data.quantity:
        raise HTTPException(400, "Недостаточно товара на складе")

    # 2. Проверяем, существует ли чек
    sale = db.query(models.Sale).filter(models.Sale.id == data.sale_id).first()
    if not sale:
        raise HTTPException(404, "Чек не найден")

    # 3. Списываем остатки
    part.stock_quantity -= data.quantity

    # 4. Создаем позицию в чеке
    sale_item = models.SaleItem(
        quantity=data.quantity,
        price_at_moment=part.price,  # Цену берем из БД, а не из запроса!
        sale_id=data.sale_id,
        part_id=data.part_id
    )
    db.add(sale_item)

    # 5. Пересчитываем сумму чека
    sale.total_price += (part.price * data.quantity)

    db.commit()
    db.refresh(sale_item)
    return sale_item