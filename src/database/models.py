# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Boolean, DateTime, func, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()


# class Record(Base):
#     __tablename__ = "records"
#     id = Column(Integer, primary_key=True)
#     first_name = Column(String(30), nullable=False)
#     last_name = Column(String(30))
#     email = Column(String(30))
#     birthday = Column(Date)
#     notes = Column(String(150))
#     created_at = Column(DateTime, default=func.now())


class Record(Base):
    __tablename__ = "records"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(30), nullable=True)
    birthday: Mapped[Date] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(String(150), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", backref="records", lazy="joined")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    pwd_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

