```
food-delivery-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application instance, global event handlers, root routes
│   ├── core/                   # Core configurations, settings, security constants
│   │   ├── __init__.py
│   │   ├── config.py           # Application settings (Pydantic BaseSettings)
│   │   ├── security.py         # JWT utilities, password hashing
│   │   └── exceptions.py       # Custom exceptions
│   ├── db/                     # Database session management, base for models
│   │   ├── __init__.py
│   │   ├── session.py          # SQLAlchemy session setup
│   │   └── base.py             # Base class for SQLAlchemy models
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── menu_item.py
│   │   ├── order.py
│   │   ├── driver.py
│   │   └── payment.py
│   ├── schemas/                # Pydantic models for request/response validation
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── menu_item.py
│   │   ├── order.py
│   │   ├── token.py            # JWT token schemas
│   │   └── common.py           # Common schemas (e.g., pagination)
│   ├── api/                    # API routers (endpoints)
│   │   ├── __init__.py
│   │   ├── deps.py             # FastAPI dependencies (e.g., get_db, get_current_user)
│   │   ├── v1/                 # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── restaurants.py
│   │   │   │   ├── menu_items.py
│   │   │   │   ├── orders.py
│   │   │   │   ├── drivers.py
│   │   │   │   └── admin.py
│   │   │   └── api.py          # Combines all v1 endpoints
│   ├── services/               # Business logic, interacts with models and external services
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── restaurant.py
│   │   ├── order.py
│   │   └── delivery.py
│   └── tests/                  # Unit and integration tests
│       ├── __init__.py
│       ├── api/
│       │   └── v1/
│       │       ├── test_auth.py
│       │       └── test_users.py
│       └── conftest.py
├── alembic/                    # Alembic migration environment
│   ├── versions/               # Migration scripts
│   └── env.py
├── alembic.ini                 # Alembic configuration
├── Dockerfile                  # Dockerfile for containerization
├── requirements.txt            # Project dependencies
├── .env.example                # Example environment variables
├── README.md
``````
fastapi==0.111.0
uvicorn[standard]==0.29.0
SQLAlchemy==2.0.30
psycopg2-binary==2.9.9
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic==2.7.1
pydantic-settings==2.2.1
redis==5.0.4
# For development and testing
pytest==8.2.1
httpx==0.27.0
``````python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class UserRole(str, Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    DRIVER = "driver"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="user", uselist=False)
    restaurant = relationship("Restaurant", back_populates="user", uselist=False)
    driver = relationship("Driver", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import User

class Customer(Base):
    __tablename__ = "customers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    default_delivery_address = Column(Text, nullable=True) # MVP: single address
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="customer")
    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer(user_id={self.user_id}, name='{self.first_name} {self.last_name}')>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import User

class RestaurantStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUSPENDED = "suspended"

class Restaurant(Base):
    __tablename__ = "restaurants"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    address = Column(Text, nullable=False)
    phone_number = Column(String, nullable=True)
    cuisine_type = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    operating_hours = Column(JSON, nullable=True) # Store as JSONB in PostgreSQL
    status = Column(Enum(RestaurantStatus), default=RestaurantStatus.PENDING_APPROVAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")

    def __repr__(self):
        return f"<Restaurant(user_id={self.user_id}, name='{self.name}')>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.restaurant import Restaurant

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.user_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', restaurant_id={self.restaurant_id})>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.customer import Customer
from app.models.restaurant import Restaurant

class OrderStatus(str, Enum):
    PLACED = "placed"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.user_id"), nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.user_id"), nullable=False)
    delivery_address = Column(Text, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PLACED)
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    delivery = relationship("Delivery", back_populates="order", uselist=False)

    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, status='{self.status}')>"

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Numeric, nullable=False)
    price_at_order = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, menu_item_id={self.menu_item_id})>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import User

class DriverStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUSPENDED = "suspended"

class Driver(Base):
    __tablename__ = "drivers"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    vehicle_info = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    status = Column(Enum(DriverStatus), default=DriverStatus.PENDING_APPROVAL)
    current_earnings = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="driver")
    deliveries = relationship("Delivery", back_populates="driver")

    def __repr__(self):
        return f"<Driver(user_id={self.user_id}, name='{self.first_name} {self.last_name}')>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.order import Order
from app.models.driver import Driver

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    FAILED = "failed"

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), unique=True, nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.user_id"), nullable=True)
    pickup_location = Column(Text, nullable=False)
    dropoff_location = Column(Text, nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    accepted_at = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    estimated_delivery_time = Column(DateTime, nullable=True)
    delivery_fee = Column(Numeric(10, 2), nullable=False)
    driver_payout = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="delivery")
    driver = relationship("Driver", back_populates="deliveries")

    def __repr__(self):
        return f"<Delivery(id={self.id}, order_id={self.order_id}, status='{self.status}')>"
``````python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.order import Order
from app.models.customer import Customer

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.user_id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String, nullable=False) # e.g., "credit_card", "stripe"
    transaction_id = Column(String, unique=True, nullable=False) # From payment gateway
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    processed_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status='{self.status}')>"
``````python
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
``````python
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    default_delivery_address: Optional[str] = None # For customer
    is_active: Optional[bool] = None # For admin

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # For SQLAlchemy 2.0
``````python
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.restaurant import RestaurantStatus

class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=3)
    address: str
    phone_number: Optional[str] = None
    cuisine_type: str
    logo_url: Optional[str] = None
    operating_hours: Optional[Dict[str, Any]] = None # e.g., {"Monday": "9:00-17:00"}

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(RestaurantBase):
    name: Optional[str] = None
    address: Optional[str] = None
    cuisine_type: Optional[str] = None
    status: Optional[RestaurantStatus] = None # For admin

class RestaurantResponse(RestaurantBase):
    user_id: uuid.UUID
    status: RestaurantStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
``````python
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str
    image_url: Optional[str] = None
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(MenuItemBase):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None

class MenuItemResponse(MenuItemBase):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
``````python
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.order import OrderStatus

class OrderItemSchema(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    restaurant_id: uuid.UUID
    delivery_address: str
    items: List[OrderItemSchema]
    special_instructions: Optional[str] = None

class OrderUpdateStatus(BaseModel):
    status: OrderStatus

class OrderItemResponse(BaseModel):
    id: uuid.UUID
    menu_item_id: uuid.UUID
    quantity: int
    price_at_order: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    restaurant_id: uuid.UUID
    delivery_address: str
    total_amount: float
    status: OrderStatus
    special_instructions: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
``````python
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str | None = None
    role: str | None = None
``````python
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenData
from app.core.exceptions import CredentialException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        if user_id is None or user_role is None:
            raise CredentialException
        token_data = TokenData(user_id=user_id, role=user_role)
    except JWTError:
        raise CredentialException
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise CredentialException
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")
    return current_user

def get_current_customer_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a customer")
    return current_user

def get_current_restaurant_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "restaurant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a restaurant")
    return current_user

def get_current_driver_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "driver":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a driver")
    return current_user
``````python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.services import user as user_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, role: UserRole, db: Session = Depends(get_db)):
    """
    Register a new user (customer, restaurant, or driver).
    """
    db_user = user_service.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = user_service.create_user(db, user_in=user_in, role=role)
    return user

@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 login to get an access token.
    """
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
``````python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user, get_current_customer_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services import user as user_service

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current active user.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_users_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current active user.
    """
    user = user_service.update_user(db, db_user=current_user, user_in=user_in)
    return user

# Admin specific endpoint
@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Retrieve users (Admin only).
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users
``````python
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_customer_user, get_current_restaurant_user, get_current_admin_user
from app.models.user import User
from app.models.restaurant import RestaurantStatus
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from app.schemas.menu_item import MenuItemResponse
from app.schemas.common import PaginatedResponse
from app.services import restaurant as restaurant_service
from app.services import menu_item as menu_item_service

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[RestaurantResponse])
def read_restaurants(
    skip: int = 0,
    limit: int = 10,
    cuisine_type: Optional[str] = Query(None, description="Filter by cuisine type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_customer_user) # Customers can browse
):
    """
    Retrieve a list of restaurants.
    """
    restaurants = restaurant_service.get_restaurants(db, skip=skip, limit=limit, cuisine_type=cuisine_type)
    total = restaurant_service.count_restaurants(db, cuisine_type=cuisine_type)
    return PaginatedResponse(items=restaurants, total=total, page=skip // limit + 1, size=limit)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def read_restaurant(
    restaurant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_customer_user)
):
    """
    Get a specific restaurant by ID.
    """
    restaurant = restaurant_service.get_restaurant(db, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant

@router.get("/{restaurant_id}/menu", response_model=List[MenuItemResponse])
def read_restaurant_menu(
    restaurant_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_customer_user)
):
    """
    Get the menu for a specific restaurant.
    """
    menu_items = menu_item_service.get_menu_items_by_restaurant(db, restaurant_id=restaurant_id)
    return menu_items

@router.put("/me", response_model=RestaurantResponse)
def update_my_restaurant_profile(
    restaurant_in: RestaurantUpdate,
    current_user: User = Depends(get_current_restaurant_user),
    db: Session = Depends(get_db)
):
    """
    Update the current restaurant's profile. (Restaurant owner only)
    """
    restaurant = restaurant_service.get_restaurant(db, restaurant_id=current_user.id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found for current user")
    updated_restaurant = restaurant_service.update_restaurant(db, db_restaurant=restaurant, restaurant_in=restaurant_in)
    return updated_restaurant

# Admin specific endpoint
@router.patch("/{restaurant_id}/status", response_model=RestaurantResponse)
def update_restaurant_status(
    restaurant_id: uuid.UUID,
    status_update: RestaurantUpdate, # Reusing for status update
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a restaurant's status (e.g., approve, suspend) (Admin only).
    """
    restaurant = restaurant_service.get_restaurant(db, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    if status_update.status is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status field is required for this operation")
    
    restaurant.status = status_update.status
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant
``````python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Food Delivery App"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str
    ASYNC_DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
``````python
from datetime import datetime, timedelta
from typing import Any
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```# Food Delivery App Backend Implementation Plan

This document details the backend implementation plan for the Food Delivery App, leveraging FastAPI, SQLAlchemy, and PostgreSQL. It covers project structure, core dependencies, data models, API design, authentication, migrations, error handling, and testing.

## 1. FastAPI Project Folder Structure

A modular and organized project structure is crucial for maintainability and scalability. We will organize the project by responsibility, as recommended by FastAPI best practices.



## 2. Core Dependencies

The `requirements.txt` file will list all necessary Python packages.



## 3. SQLAlchemy Models

We will use SQLAlchemy 2.0 with `declarative_base` for defining ORM models. UUIDs will be used for primary keys.

**`app/db/base.py`**



**`app/models/user.py`**



**`app/models/customer.py`**



**`app/models/restaurant.py`**



**`app/models/menu_item.py`**



**`app/models/order.py`**



**`app/models/driver.py`**



**`app/models/delivery.py`**



**`app/models/payment.py`**



## 4. Pydantic Schemas

Pydantic schemas define the data shapes for API requests and responses, ensuring validation and clear contracts.

**`app/schemas/common.py`**



**`app/schemas/user.py`**



**`app/schemas/restaurant.py`**



**`app/schemas/menu_item.py`**



**`app/schemas/order.py`**



**`app/schemas/token.py`**



## 5. CRUD API Design

API endpoints will be organized by resource and versioned. We'll use FastAPI's `APIRouter`.

**`app/api/deps.py`** (Database session and current user dependency)



**`app/api/v1/endpoints/auth.py`** (Authentication routes)



**`app/api/v1/endpoints/users.py`** (User-specific routes)



**`app/api/v1/endpoints/restaurants.py`** (Restaurant-specific routes)



## 6. JWT Authentication Flow

The JWT authentication flow involves user registration, login to obtain tokens, and using these tokens to access protected routes.

1.  **User Registration:**
    *   A user (Customer, Restaurant, Driver) sends a `POST` request to `/api/v1/auth/register` with their email, password, and desired role.
    *   The backend hashes the password using `bcrypt` and stores the user in the `users` table.
    *   A corresponding entry is created in `customers`, `restaurants`, or `drivers` table.
2.  **User Login:**
    *   A user sends a `POST` request to `/api/v1/auth/login` with their email and password.
    *   The backend verifies the password against the stored hash.
    *   If successful, a JWT `access_token` is generated using `python-jose`. The token payload includes `user_id` and `role`.
    *   The `access_token` has a short expiry (e.g., 15 minutes).
    *   The `access_token` is returned to the client.
3.  **Accessing Protected Routes:**
    *   For subsequent requests to protected endpoints, the client includes the `access_token` in the `Authorization` header as `Bearer <token>`.
    *   FastAPI's `OAuth2PasswordBearer` and a custom dependency (`get_current_user`) extract and validate the token.
    *   The token is decoded, its signature is verified using `settings.SECRET_KEY`, and its expiry is checked.
    *   The `user_id` and `role` from the token payload are used to fetch the `User` object from the database.
    *   Role-based authorization dependencies (`get_current_customer_user`, `get_current_restaurant_user`, etc.) then check if the authenticated user has the necessary role for the requested action.

**`app/core/config.py`** (Settings for JWT)



**`app/core/security.py`** (JWT and password hashing utilities)



## 7. Alembic Migration Plan

Alembic will be used to manage database schema migrations, ensuring that changes to SQLAlchemy models are reflected in the PostgreSQL database in a controlled and repeatable manner.

**Setup:**

1.  **Install Alembic:** `pip install alembic`
2.  **Initialize Alembic:**
    ```bash
    alembic init alembic
    ```
    This creates the `alembic/` directory and `alembic.ini`.
3.  **Configure `alembic.ini`:**
    *   Set `sqlalchemy.url` to your database connection string (e.g., `postgresql://user:password@host:port/dbname`).
    *   Ensure `script_location` points to `alembic`.
4.  **Configure `alembic/env.py`:**
    *   Import your SQLAlchemy `Base` from `app.db.base`.
    *   Set `target_metadata = Base.metadata`.
    *   Ensure the `run_migrations_online` function uses the correct database URL.

    ```python
    # alembic/env.py (excerpt)
    from logging.config import fileConfig
    from sqlalchemy import engine_from_config, pool
    from alembic import context

    # This is the Base from your models
    from app.db.base import Base
    from app.models import user, customer, restaurant, menu_item, order, driver, delivery, payment # Import all models

    # ... other imports and configurations ...

    # target_metadata should be the Base.metadata from your SQLAlchemy models
    target_metadata = Base.metadata

    # ... rest of the file ...
    ```

**Migration Workflow:**

1.  **Create a new migration script:** After making changes to your SQLAlchemy models (e.g., adding a new table, modifying a column), generate a migration script:
    ```bash
    alembic revision --autogenerate -m "Add initial tables"
    ```
    Alembic will compare your models with the current database schema and generate a Python script in `alembic/versions/` with `upgrade()` and `downgrade()` functions.
2.  **Review the migration script:** **Always review** the generated script to ensure it accurately reflects your intended changes. Manually adjust if necessary.
3.  **Apply migrations:** Apply the pending migrations to your database:
    ```bash
    alembic upgrade head
    ```
    This will run all `upgrade()` functions from the new and any unapplied scripts.
4.  **Downgrade (if needed):** To revert the last migration:
    ```bash
    alembic downgrade -1
    ```
    Or to a specific revision:
    ```bash
    alembic downgrade <revision_id>
    ```

## 8. Error Handling Strategy

A consistent error handling strategy improves API usability and maintainability.

*   **FastAPI's `HTTPException`:** For common HTTP errors (400, 401, 403, 404), use `raise HTTPException(status_code=..., detail=...)`. FastAPI will automatically convert these into JSON responses.
*   **Custom Exceptions:** For domain-specific errors, define custom exceptions.
    *   **`app/core/exceptions.py`**
        ```python
        from fastapi import HTTPException, status

        class CredentialException(HTTPException):
            def __init__(self):
                super().__init__(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        class UserNotFoundException(HTTPException):
            def __init__(self):
                super().__init__(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

        class RestaurantNotFoundException(HTTPException):
            def __init__(self):
                super().__init__(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Restaurant not found",
                )

        class OrderNotFoundException(HTTPException):
            def __init__(self):
                super().__init__(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found",
                )

        class UnauthorizedActionException(HTTPException):
            def __init__(self):
                super().__init__(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to perform this action",
                )
        ```
*   **Global Exception Handlers:** For unhandled exceptions or custom exceptions that need specific handling, register global exception handlers in `app/main.py`.

    ```python
    # app/main.py (excerpt)
    from fastapi import FastAPI, Request, status
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from app.core.exceptions import CredentialException, UserNotFoundException # etc.

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Global exception handlers
    @app.exception_handler(CredentialException)
    async def credential_exception_handler(request: Request, exc: CredentialException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "headers": exc.headers}
        )

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": exc.body}
        )

    # Generic handler for unhandled exceptions
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."}
        )
    ``````python
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from app.main import app
from app.models.user import UserRole
from app.schemas.user import UserCreate

client = TestClient(app)

def test_register_customer(db: Session):
    email = "test_customer@example.com"
    password = "securepassword"
    user_in = UserCreate(email=email, password=password, role=UserRole.CUSTOMER)
    response = client.post(
        f"{settings.API_V1_STR}/auth/register?role={UserRole.CUSTOMER.value}",
        json=user_in.model_dump()
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["role"] == UserRole.CUSTOMER.value
    assert "id" in data

def test_login_customer(db: Session):
    email = "login_customer@example.com"
    password = "securepassword"
    user_in = UserCreate(email=email, password=password, role=UserRole.CUSTOMER)
    client.post(
        f"{settings.API_V1_STR}/auth/register?role={UserRole.CUSTOMER.value}",
        json=user_in.model_dump()
    )

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_incorrect_password(db: Session):
    email = "wrong_pass@example.com"
    password = "securepassword"
    user_in = UserCreate(email=email, password=password, role=UserRole.CUSTOMER)
    client.post(
        f"{settings.API_V1_STR}/auth/register?role={UserRole.CUSTOMER.value}",
        json=user_in.model_dump()
    )

    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_unregistered_email(db: Session):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
```

## 9. Backend Test Plan

A comprehensive test plan ensures the reliability and correctness of the backend.

*   **Unit Tests:**
    *   **Scope:** Individual functions, methods, and classes in `app/services/`, `app/core/security.py`, etc.
    *   **Tools:** `pytest`.
    *   **Mocks:** Use `unittest.mock` to mock external dependencies (e.g., database calls, external API calls) to isolate the unit under test.
    *   **Examples:**
        *   Test password hashing and verification.
        *   Test JWT token creation and decoding.
        *   Test service functions (e.g., `create_user`, `get_user_by_email`) with mocked database sessions.
*   **Integration Tests:**
    *   **Scope:** Interactions between different components (e.g., API endpoints with services and database).
    *   **Tools:** `pytest`, `httpx` (for making HTTP requests to the FastAPI app).
    *   **Database:** Use a dedicated test database (e.g., an in-memory SQLite database or a separate PostgreSQL test database) that is reset before each test run.
    *   **Examples:**
        *   Test user registration and login flow, ensuring tokens are returned and valid.
        *   Test CRUD operations for a resource (e.g., creating a restaurant, retrieving it, updating it, deleting it).
        *   Test authorization rules (e.g., a customer trying to access an admin endpoint).
        *   Test pagination and filtering on list endpoints.
*   **End-to-End (E2E) Tests:**
    *   **Scope:** Simulate real user scenarios across the entire system, including the API and potentially external services (mocked).
    *   **Tools:** `pytest`, `httpx`.
    *   **Database:** Use a clean test database.
    *   **Examples:**
        *   Customer registers, logs in, browses restaurants, adds items to cart, places an order.
        *   Restaurant owner logs in, adds a menu item, accepts an order.
        *   Delivery driver logs in, accepts a delivery, updates status to delivered.
*   **Test Data:**
    *   Use factories (e.g., `Faker` with `factory_boy`) to generate realistic but reproducible test data.
    *   Ensure test data is isolated between tests.
*   **CI/CD Integration:**
    *   Automate test execution as part of the CI/CD pipeline. All tests must pass before deployment.
*   **Code Coverage:**
    *   Use `pytest-cov` to measure test coverage and aim for a high percentage (e.g., >80%).

**Example `app/tests/api/v1/test_auth.py`**

