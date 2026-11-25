from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from datetime import datetime
import re

class RegisterIn(BaseModel):
    username: str = Field(min_length = 3, max_length = 50)
    password: str = Field(min_length = 6)
    role: str = Field(default = "user")
    avatar_url: Optional[str] = None
    email: Optional[str] = None

class RegisterOut(BaseModel):
    id: int
    username: str
    role: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class LogIn(BaseModel):
    username: str
    password: str


class SupplierIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

    # Используем EmailStr для проверки почты и pattern для телефона
    contact_info: str = Field(..., description="Телефон или Email")
    user_id: int

    # ВАЛИДАЦИЯ: Проверяем, что это либо правильный телефон, либо правильный email
    @field_validator('contact_info')
    @classmethod
    def validate_contact_info(cls, v):
        # Проверка на email (простая регулярка: текст @ текст . текст)
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        # Проверка на телефон РФ (+7 или 8, 11 цифр, можно с пробелами/скобками/дефисами)
        phone_pattern = r'^(\+7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'

        digits_only = re.sub(r'\D', '', v)

        if re.match(email_pattern, v):
            return v
        elif re.match(phone_pattern, v) or (len(digits_only) in [10, 11] and digits_only.isdigit()):
            return v
        else:
            raise ValueError('Введите корректный номер телефона (11 цифр) или Email (example@mail.ru)')

class SupplierOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    contact_info: str
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class SupplierPatch(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    user_id: Optional[int] = None

class SaleItemIn(BaseModel):
    quantity: int = Field(gt = 0)
    price_at_moment: Decimal = Field(ge = 0, max_digits = 8,decimal_places = 2)
    sale_id: int
    part_id: int

class SaleItemOut(BaseModel):
    id: int
    sale_id: int
    part_id: int
    quantity: int
    price_at_moment: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class SaleItemPatch(BaseModel):
    quantity: Optional[int] = None
    price_at_moment: Optional[Decimal] = None
    sale_id: Optional[int] = None
    part_id: Optional[int] = None

class SaleIn(BaseModel):
    total_price: Decimal = Field(ge = 0, max_digits = 8, decimal_places = 2)
    seller_id: int

class SaleOut(BaseModel):
    id: int
    seller_id: int
    total_price: Decimal
    items: list[SaleItemOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class SalePatch(BaseModel):
    total_price: Optional[Decimal] = None

class BrandIn(BaseModel):
    name: str

class BrandOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes = True)

class BrandPatch(BaseModel):
    name: Optional[str] = None

class CarModelIn(BaseModel):
    name: str
    brand_id: int

class CarModelOut(BaseModel):
    id: int
    name: str
    brand_id: int

    model_config = ConfigDict(from_attributes = True)

class CarModelPatch(BaseModel):
    name: Optional[str] = None
    brand_id: Optional[int] = None

class PartIn(BaseModel):
    article: str
    name: str
    price: Decimal = Field(ge = 0, max_digits = 8, decimal_places = 2)
    stock_quantity: int = Field(ge = 0)
    supplier_id: Optional[int] = None

class PartOut(BaseModel):
    id: int
    supplier_id: int
    article: str
    name: str
    price: Decimal
    stock_quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class PartPatch(BaseModel):
    article: Optional[str] = None
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None

class AnalogIn(BaseModel):
    part_id: int
    analog_part_id: int

class AnalogOut(BaseModel):
    id: int
    part_id: int
    analog_part_id: int

    model_config = ConfigDict(from_attributes = True)

class AnalogPatch(BaseModel):
    part_id: Optional[int] = None
    analog_part_id: Optional[int] = None

class PartModelIn(BaseModel):
    part_id: int
    car_model_id: int

class PartModelOut(BaseModel):
    id: int
    part_id: int
    car_model_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class PartModelPatch(BaseModel):
    part_id: Optional[int] = None
    car_model_id: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

