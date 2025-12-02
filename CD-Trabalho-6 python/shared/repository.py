"""
Repositório compartilhado usando SQLAlchemy e PostgreSQL
"""
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
import uuid
from shared.models import Base, UsuarioDB, MusicaDB, PlaylistDB, Usuario, Musica, Playlist


class Repositorio:
    """Repositório para gerenciar operações CRUD no banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== USUÁRIOS ==========
    
    def criar_usuario(self, usuario: Usuario) -> Usuario:
        """Cria um novo usuário"""
        usuario_db = UsuarioDB(
            id=usuario.id if usuario.id else str(uuid.uuid4()),
            nome=usuario.nome,
            idade=usuario.idade
        )
        self.db.add(usuario_db)
        self.db.commit()
        self.db.refresh(usuario_db)
        return Usuario.model_validate(usuario_db)
    
    def obter_usuario(self, id: str) -> Optional[Usuario]:
        """Obtém um usuário por ID"""
        usuario_db = self.db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
        return Usuario.model_validate(usuario_db) if usuario_db else None
    
    def listar_usuarios(self) -> List[Usuario]:
        """Lista todos os usuários"""
        usuarios_db = self.db.query(UsuarioDB).all()
        return [Usuario.model_validate(u) for u in usuarios_db]
    
    def atualizar_usuario(self, id: str, dados: dict) -> Optional[Usuario]:
        """Atualiza um usuário"""
        usuario_db = self.db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
        if not usuario_db:
            return None
        
        for key, value in dados.items():
            if hasattr(usuario_db, key):
                setattr(usuario_db, key, value)
        
        self.db.commit()
        self.db.refresh(usuario_db)
        return Usuario.model_validate(usuario_db)
    
    def remover_usuario(self, id: str) -> bool:
        """Remove um usuário e todas suas playlists (cascade)"""
        usuario_db = self.db.query(UsuarioDB).filter(UsuarioDB.id == id).first()
        if not usuario_db:
            return False
        
        self.db.delete(usuario_db)
        self.db.commit()
        return True
    
    # ========== MÚSICAS ==========
    
    def criar_musica(self, musica: Musica) -> Musica:
        """Cria uma nova música"""
        musica_db = MusicaDB(
            id=musica.id if musica.id else str(uuid.uuid4()),
            nome=musica.nome,
            artista=musica.artista
        )
        self.db.add(musica_db)
        self.db.commit()
        self.db.refresh(musica_db)
        return Musica.model_validate(musica_db)
    
    def obter_musica(self, id: str) -> Optional[Musica]:
        """Obtém uma música por ID"""
        musica_db = self.db.query(MusicaDB).filter(MusicaDB.id == id).first()
        return Musica.model_validate(musica_db) if musica_db else None
    
    def listar_musicas(self) -> List[Musica]:
        """Lista todas as músicas"""
        musicas_db = self.db.query(MusicaDB).all()
        return [Musica.model_validate(m) for m in musicas_db]
    
    def atualizar_musica(self, id: str, dados: dict) -> Optional[Musica]:
        """Atualiza uma música"""
        musica_db = self.db.query(MusicaDB).filter(MusicaDB.id == id).first()
        if not musica_db:
            return None
        
        for key, value in dados.items():
            if hasattr(musica_db, key):
                setattr(musica_db, key, value)
        
        self.db.commit()
        self.db.refresh(musica_db)
        return Musica.model_validate(musica_db)
    
    def remover_musica(self, id: str) -> bool:
        """Remove uma música (será removida de todas as playlists automaticamente)"""
        musica_db = self.db.query(MusicaDB).filter(MusicaDB.id == id).first()
        if not musica_db:
            return False
        
        self.db.delete(musica_db)
        self.db.commit()
        return True
    
    # ========== PLAYLISTS ==========
    
    def criar_playlist(self, playlist: Playlist) -> Playlist:
        """Cria uma nova playlist"""
        # Valida se o usuário existe
        usuario_db = self.db.query(UsuarioDB).filter(UsuarioDB.id == playlist.usuario_id).first()
        if not usuario_db:
            raise ValueError('Usuário não encontrado')
        
        playlist_db = PlaylistDB(
            id=playlist.id if playlist.id else str(uuid.uuid4()),
            nome=playlist.nome,
            usuario_id=playlist.usuario_id
        )
        
        # Adiciona músicas se fornecidas
        if playlist.musicas_ids:
            musicas_db = self.db.query(MusicaDB).filter(MusicaDB.id.in_(playlist.musicas_ids)).all()
            if len(musicas_db) != len(playlist.musicas_ids):
                raise ValueError('Uma ou mais músicas não foram encontradas')
            playlist_db.musicas = musicas_db
        
        self.db.add(playlist_db)
        self.db.commit()
        self.db.refresh(playlist_db)
        
        return Playlist(
            id=playlist_db.id,
            nome=playlist_db.nome,
            usuario_id=playlist_db.usuario_id,
            musicas_ids=[m.id for m in playlist_db.musicas]
        )
    
    def obter_playlist(self, id: str) -> Optional[Playlist]:
        """Obtém uma playlist por ID"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlist_db = self.db.query(PlaylistDB).filter(PlaylistDB.id == id).options(selectinload(PlaylistDB.musicas)).first()
        if not playlist_db:
            return None
        
        return Playlist(
            id=playlist_db.id,
            nome=playlist_db.nome,
            usuario_id=playlist_db.usuario_id,
            musicas_ids=[m.id for m in playlist_db.musicas]
        )
    
    def listar_playlists(self) -> List[Playlist]:
        """Lista todas as playlists"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlists_db = self.db.query(PlaylistDB).options(selectinload(PlaylistDB.musicas)).all()
        return [
            Playlist(
                id=p.id,
                nome=p.nome,
                usuario_id=p.usuario_id,
                musicas_ids=[m.id for m in p.musicas]
            )
            for p in playlists_db
        ]
    
    def listar_playlists_por_usuario(self, usuario_id: str) -> List[Playlist]:
        """Lista playlists de um usuário"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlists_db = self.db.query(PlaylistDB).filter(PlaylistDB.usuario_id == usuario_id).options(selectinload(PlaylistDB.musicas)).all()
        return [
            Playlist(
                id=p.id,
                nome=p.nome,
                usuario_id=p.usuario_id,
                musicas_ids=[m.id for m in p.musicas]
            )
            for p in playlists_db
        ]
    
    def listar_musicas_por_playlist(self, playlist_id: str) -> List[Musica]:
        """Lista músicas de uma playlist"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlist_db = self.db.query(PlaylistDB).filter(PlaylistDB.id == playlist_id).options(selectinload(PlaylistDB.musicas)).first()
        if not playlist_db:
            return []
        
        return [Musica.model_validate(m) for m in playlist_db.musicas]
    
    def listar_playlists_por_musica(self, musica_id: str) -> List[Playlist]:
        """Lista playlists que contêm uma música"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        musica_db = self.db.query(MusicaDB).filter(MusicaDB.id == musica_id).options(selectinload(MusicaDB.playlists).selectinload(PlaylistDB.musicas)).first()
        if not musica_db:
            return []
        
        return [
            Playlist(
                id=p.id,
                nome=p.nome,
                usuario_id=p.usuario_id,
                musicas_ids=[m.id for m in p.musicas]
            )
            for p in musica_db.playlists
        ]
    
    def atualizar_playlist(self, id: str, dados: dict) -> Optional[Playlist]:
        """Atualiza uma playlist"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlist_db = self.db.query(PlaylistDB).filter(PlaylistDB.id == id).options(selectinload(PlaylistDB.musicas)).first()
        if not playlist_db:
            return None
        
        # Valida usuário se estiver sendo alterado
        if 'usuario_id' in dados:
            usuario_db = self.db.query(UsuarioDB).filter(UsuarioDB.id == dados['usuario_id']).first()
            if not usuario_db:
                raise ValueError('Usuário não encontrado')
            playlist_db.usuario_id = dados['usuario_id']
        
        if 'nome' in dados:
            playlist_db.nome = dados['nome']
        
        self.db.commit()
        self.db.refresh(playlist_db)
        
        return Playlist(
            id=playlist_db.id,
            nome=playlist_db.nome,
            usuario_id=playlist_db.usuario_id,
            musicas_ids=[m.id for m in playlist_db.musicas]
        )
    
    def adicionar_musica_a_playlist(self, playlist_id: str, musica_id: str) -> Optional[Playlist]:
        """Adiciona uma música a uma playlist"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlist_db = self.db.query(PlaylistDB).filter(PlaylistDB.id == playlist_id).options(selectinload(PlaylistDB.musicas)).first()
        if not playlist_db:
            return None
        
        musica_db = self.db.query(MusicaDB).filter(MusicaDB.id == musica_id).first()
        if not musica_db:
            raise ValueError('Música não encontrada')
        
        # Evita duplicatas
        if musica_db not in playlist_db.musicas:
            playlist_db.musicas.append(musica_db)
            self.db.commit()
            self.db.refresh(playlist_db)
        
        return Playlist(
            id=playlist_db.id,
            nome=playlist_db.nome,
            usuario_id=playlist_db.usuario_id,
            musicas_ids=[m.id for m in playlist_db.musicas]
        )
    
    def remover_musica_de_playlist(self, playlist_id: str, musica_id: str) -> Optional[Playlist]:
        """Remove uma música de uma playlist"""
        # Usa selectinload para muitos-para-muitos (evita produto cartesiano)
        playlist_db = self.db.query(PlaylistDB).filter(PlaylistDB.id == playlist_id).options(selectinload(PlaylistDB.musicas)).first()
        if not playlist_db:
            return None
        
        musica_db = self.db.query(MusicaDB).filter(MusicaDB.id == musica_id).first()
        if not musica_db:
            return None
        
        if musica_db in playlist_db.musicas:
            playlist_db.musicas.remove(musica_db)
            self.db.commit()
            self.db.refresh(playlist_db)
        
        return Playlist(
            id=playlist_db.id,
            nome=playlist_db.nome,
            usuario_id=playlist_db.usuario_id,
            musicas_ids=[m.id for m in playlist_db.musicas]
        )
    
    def remover_playlist(self, id: str) -> bool:
        """Remove uma playlist"""
        playlist_db = self.db.query(PlaylistDB).filter(PlaylistDB.id == id).first()
        if not playlist_db:
            return False
        
        self.db.delete(playlist_db)
        self.db.commit()
        return True

