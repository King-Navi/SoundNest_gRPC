from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = 'Role'
    __table_args__ = (
        Index('roleName', 'roleName', unique=True),
    )

    idRole: Mapped[int] = mapped_column(Integer, primary_key=True)
    roleName: Mapped[str] = mapped_column(String(100))

    AppUser: Mapped[List['AppUser']] = relationship('AppUser', back_populates='Role_')


class SongGenre(Base):
    __tablename__ = 'SongGenre'

    idSongGenre: Mapped[int] = mapped_column(Integer, primary_key=True)
    genreName: Mapped[Optional[str]] = mapped_column(String(100))

    Song: Mapped[List['Song']] = relationship('Song', back_populates='SongGenre_')


class AppUser(Base):
    __tablename__ = 'AppUser'
    __table_args__ = (
        ForeignKeyConstraint(['idRole'], ['Role.idRole'], name='AppUser_ibfk_1'),
        Index('email', 'email', unique=True),
        Index('idRole', 'idRole'),
        Index('nameUser', 'nameUser', unique=True)
    )

    idUser: Mapped[int] = mapped_column(Integer, primary_key=True)
    nameUser: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(100))
    idRole: Mapped[int] = mapped_column(Integer)

    Role_: Mapped['Role'] = relationship('Role', back_populates='AppUser')
    Photo: Mapped[List['Photo']] = relationship('Photo', back_populates='AppUser_')
    Song: Mapped[List['Song']] = relationship('Song', back_populates='AppUser_')


class Photo(Base):
    __tablename__ = 'Photo'
    __table_args__ = (
        ForeignKeyConstraint(['idUser'], ['AppUser.idUser'], name='Photo_ibfk_1'),
        Index('idUser', 'idUser')
    )

    idPhoto: Mapped[int] = mapped_column(Integer, primary_key=True)
    fileName: Mapped[str] = mapped_column(String(100))
    extension: Mapped[str] = mapped_column(String(50))
    createdAt: Mapped[datetime.datetime] = mapped_column(DateTime)
    idUser: Mapped[int] = mapped_column(Integer)

    AppUser_: Mapped['AppUser'] = relationship('AppUser', back_populates='Photo')


class Song(Base):
    __tablename__ = 'Song'
    __table_args__ = (
        ForeignKeyConstraint(['idAppUser'], ['AppUser.idUser'], name='Song_ibfk_2'),
        ForeignKeyConstraint(['idSongGenre'], ['SongGenre.idSongGenre'], name='Song_ibfk_1'),
        Index('idAppUser', 'idAppUser'),
        Index('idSongGenre', 'idSongGenre')
    )

    idSong: Mapped[int] = mapped_column(Integer, primary_key=True)
    songName: Mapped[str] = mapped_column(String(100))
    filePath: Mapped[str] = mapped_column(String(255))
    durationSeconds: Mapped[int] = mapped_column(Integer)
    releaseDate: Mapped[datetime.datetime] = mapped_column(DateTime)
    idSongGenre: Mapped[int] = mapped_column(Integer)
    idAppUser: Mapped[int] = mapped_column(Integer)

    AppUser_: Mapped['AppUser'] = relationship('AppUser', back_populates='Song')
    SongGenre_: Mapped['SongGenre'] = relationship('SongGenre', back_populates='Song')
    Visualization: Mapped[List['Visualization']] = relationship('Visualization', back_populates='Song_')


class Visualization(Base):
    __tablename__ = 'Visualization'
    __table_args__ = (
        ForeignKeyConstraint(['idSong'], ['Song.idSong'], name='Visualization_ibfk_1'),
        Index('idSong', 'idSong')
    )

    idVisualizations: Mapped[int] = mapped_column(Integer, primary_key=True)
    playCount: Mapped[int] = mapped_column(Integer)
    period: Mapped[datetime.date] = mapped_column(Date)
    idSong: Mapped[int] = mapped_column(Integer)

    Song_: Mapped['Song'] = relationship('Song', back_populates='Visualization')
