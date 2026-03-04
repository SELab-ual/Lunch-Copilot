
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey

class Base(DeclarativeBase):
    pass

class RestaurantType(Base):
    __tablename__ = 'restaurant_types'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    restaurants: Mapped[list['Restaurant']] = relationship(back_populates='type')

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    average_price: Mapped[int] = mapped_column(Integer, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    type_id: Mapped[int] = mapped_column(ForeignKey('restaurant_types.id'), nullable=False)
    type: Mapped[RestaurantType] = relationship(back_populates='restaurants')
