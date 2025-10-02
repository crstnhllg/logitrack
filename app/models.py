from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum,
    Boolean,
)
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    role = Column(Enum("admin", "driver", name="role_name"), nullable=False)
    hashed_password = Column(String, nullable=False)

    vehicles = relationship("Vehicle", back_populates="user", cascade="all, delete")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    license_plate = Column(String(15), nullable=False)
    type = Column(
        Enum("motorcycle", "sedan", "pickup", "van", "truck", name="vehicle_type")
    )
    capacity_kg = Column(Integer, nullable=False)
    status = Column(
        Enum("available", "on_route", "maintenance", "inactive", name="vehicle_status"),
        nullable=False,
    )
    driver_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    user = relationship("User", back_populates="vehicles")
    orders = relationship("Order", back_populates="vehicle", cascade="all, delete")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    destination = Column(String, nullable=False)
    size = Column(Enum("xs", "s", "m", "l", "xl", name="package_size"), nullable=False)
    priority = Column(Boolean, nullable=False)
    delivery_window_start = Column(DateTime, nullable=False)
    delivery_window_end = Column(DateTime, nullable=False)
    status = Column(
        Enum("pending", "in_transit", "completed", "failed", name="delivery_status"),
        nullable=False,
    )
    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    vehicle = relationship("Vehicle", back_populates="orders")
