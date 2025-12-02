"""
Modelos de dados compartilhados entre todas as implementações
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime

Base = declarative_base()

# Tabela de associação muitos-para-muitos entre Playlist e Musica
playlist_musica = Table(
    'playlist_musica',
    Base.metadata,
    Column('playlist_id', String, ForeignKey('playlists.id'), primary_key=True),
    Column('musica_id', String, ForeignKey('musicas.id'), primary_key=True)
)


class UsuarioDB(Base):
    """Modelo de banco de dados para Usuário"""
    __tablename__ = 'usuarios'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String, nullable=False)
    idade = Column(Integer, nullable=False)
    
    # Relacionamento com playlists
    playlists = relationship('PlaylistDB', back_populates='usuario', cascade='all, delete-orphan')


class MusicaDB(Base):
    """Modelo de banco de dados para Música"""
    __tablename__ = 'musicas'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String, nullable=False)
    artista = Column(String, nullable=False)
    
    # Relacionamento muitos-para-muitos com playlists
    playlists = relationship('PlaylistDB', secondary=playlist_musica, back_populates='musicas')


class PlaylistDB(Base):
    """Modelo de banco de dados para Playlist"""
    __tablename__ = 'playlists'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String, nullable=False)
    usuario_id = Column(String, ForeignKey('usuarios.id'), nullable=False)
    
    # Relacionamentos
    usuario = relationship('UsuarioDB', back_populates='playlists')
    musicas = relationship('MusicaDB', secondary=playlist_musica, back_populates='playlists')


# Modelos Pydantic para validação e serialização
class Usuario(BaseModel):
    id: Optional[str] = None
    nome: str
    idade: int
    
    class Config:
        from_attributes = True


class Musica(BaseModel):
    id: Optional[str] = None
    nome: str
    artista: str
    
    class Config:
        from_attributes = True


class Playlist(BaseModel):
    id: Optional[str] = None
    nome: str
    usuario_id: str
    musicas_ids: List[str] = []
    
    class Config:
        from_attributes = True

