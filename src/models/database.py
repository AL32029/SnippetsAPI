import uuid
from uuid import uuid7

from sqlalchemy import (
    UUID,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    false,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    password_hash: Mapped[str] = mapped_column(String(255))

    snippets: Mapped[list["SnippetORM"]] = relationship(
        "SnippetORM",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SnippetORM(Base):
    __tablename__ = "snippets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(96))
    language: Mapped[str] = mapped_column(String(48))
    code: Mapped[str] = mapped_column(Text)

    user: Mapped["UserORM"] = relationship("UserORM", back_populates="snippets")
    public_urls: Mapped[list["SnippetURLORM"]] = relationship(
        "SnippetURLORM",
        back_populates="snippet",
        lazy="noload",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SnippetURLORM(Base):
    __tablename__ = "snippet_urls"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        default=uuid7,
        server_default=text("uuidv7()"),
    )
    snippet_id: Mapped[int] = mapped_column(
        ForeignKey("snippets.id", ondelete="CASCADE"),
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
    )

    snippet: Mapped["SnippetORM"] = relationship(
        "SnippetORM",
        back_populates="public_urls",
        lazy="joined",
    )
