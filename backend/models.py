from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, Text, DateTime, Index, Numeric
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    username = Column(String(100), nullable = False, unique = True)
    password_hash = Column(String(255), nullable = False)
    role = Column(String(20), default = "user")
    avatar_url = Column(Text)
    email = Column(String(100), unique = True)
    created_at = Column(DateTime, default = datetime.now)

    suppliers = relationship("Supplier", back_populates = "users", cascade = "all, delete-orphan")
    sales = relationship("Sale", back_populates = "users", cascade = "all, delete-orphan")

    __table_args__ = (
        Index("idx_user_role", "role"),
        CheckConstraint("role IN ('user', 'supplier', 'admin', 'seller')", "ck_role")
    )

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False, unique = True)
    contact_info = Column(String(150), nullable = False)
    created_at = Column(DateTime, default = datetime.now)

    user_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)

    users = relationship("User", back_populates = "suppliers")
    parts = relationship("Part", back_populates = "suppliers")

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False, unique = True)

    car_models = relationship("CarModel", back_populates = "brands", cascade = "all, delete-orphan")

class CarModel(Base):
    __tablename__ = "car_models"
    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)

    brand_id = Column(Integer, ForeignKey("brands.id", ondelete = "CASCADE"), nullable = False)

    brands = relationship("Brand", back_populates = "car_models")
    parts_models = relationship("PartModel", back_populates = "car_models", cascade = "all, delete-orphan")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key = True)
    total_price = Column(Numeric(8,2), nullable = False)
    created_at = Column(DateTime, default = datetime.now)

    seller_id = Column(Integer, ForeignKey("users.id", ondelete = "CASCADE"), nullable = False)
    users = relationship("User", back_populates = "sales")
    sale_items = relationship("SaleItem", back_populates = "sales", cascade = "all, delete-orphan")

    __table_args__ = (
        Index("idx_sale_price", "total_price"),
        CheckConstraint("total_price >= 0", "ck_sale_price")
    )

class Part(Base):
    __tablename__ = "parts"
    id = Column(Integer, primary_key = True)
    article = Column(String(100), unique = True, nullable = False)
    name = Column(String(100), nullable = False)
    price = Column(Numeric(8,2), nullable = False)
    stock_quantity = Column(Integer, nullable = False)
    created_at = Column(DateTime, default = datetime.now)

    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete = "CASCADE"), nullable = False)

    suppliers = relationship("Supplier", back_populates = "parts")
    parts_models = relationship("PartModel", back_populates = "parts", cascade = "all, delete-orphan")
    analogs = relationship("Analog", foreign_keys = "[Analog.part_id]", back_populates = "part", cascade = "all, delete-orphan")
    sale_items = relationship("SaleItem", back_populates = "parts", cascade = "all, delete-orphan")

    __table_args__ = (
        Index("idx_part_price", "price"),
        Index("idx_part_quantity", "stock_quantity"),
        CheckConstraint("price >= 0", "ck_part_price"),
        CheckConstraint("stock_quantity >= 0", "ck_part_quantity")
    )

class PartModel(Base):
    __tablename__ = "parts_models"
    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default = datetime.now)

    part_id = Column(ForeignKey("parts.id", ondelete = "CASCADE"), nullable = False)
    car_model_id = Column(ForeignKey("car_models.id", ondelete = "CASCADE"), nullable = False)

    parts = relationship("Part", back_populates = "parts_models")
    car_models = relationship("CarModel", back_populates = "parts_models")

class Analog(Base):
    __tablename__ = "analogs"
    id = Column(Integer, primary_key = True)

    part_id = Column(Integer, ForeignKey("parts.id", ondelete = "CASCADE"), nullable = False)
    analog_part_id = Column(Integer, ForeignKey("parts.id", ondelete = "CASCADE"), nullable = False)

    part = relationship("Part", foreign_keys= [part_id], back_populates = "analogs")
    analog_part = relationship("Part", foreign_keys = [analog_part_id])

    __table_args__ = (
        Index("idx_part_id", "part_id"),
        Index("idx_analog_part_id", "analog_part_id"),
        CheckConstraint("part_id != analog_part_id", "ck_not_self_analog")
    )

class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key = True)
    quantity = Column(Integer, nullable = False)
    price_at_moment = Column(Numeric(8,2), nullable = False)
    created_at = Column(DateTime, default = datetime.now)

    sale_id = Column(Integer, ForeignKey("sales.id", ondelete = "CASCADE"), nullable = False)
    part_id = Column(Integer, ForeignKey("parts.id", ondelete = "RESTRICT"), nullable = False)

    sales = relationship("Sale", back_populates = "sale_items")
    parts = relationship("Part", back_populates = "sale_items")

    __table_args__ = (
        Index("idx_sale_item_quantity", "quantity"),
        Index("idx_sale_item_price", "price_at_moment"),
        CheckConstraint("quantity > 0", "ck_quantity"),
        CheckConstraint("price_at_moment >= 0", "ck_price")
    )