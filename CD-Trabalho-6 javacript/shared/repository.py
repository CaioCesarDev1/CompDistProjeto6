"""
Repositório em memória - versão simplificada
"""
from typing import Optional, List, Dict
from shared.models import Usuario, Musica, Playlist, gerar_id


class Repositorio:
    """Repositório em memória para gerenciar operações CRUD"""
    
    def __init__(self):
        # Armazenamento em memória usando dicionários
        self._usuarios: Dict[str, Usuario] = {}
        self._musicas: Dict[str, Musica] = {}
        self._playlists: Dict[str, Playlist] = {}
    
    # ========== USUÁRIOS ==========
    
    def criar_usuario(self, nome: str, idade: int, id: Optional[str] = None) -> Usuario:
        """Cria um novo usuário"""
        usuario = Usuario(
            id=id or gerar_id(),
            nome=nome,
            idade=idade
        )
        self._usuarios[usuario.id] = usuario
        return usuario
    
    def obter_usuario(self, id: str) -> Optional[Usuario]:
        """Obtém um usuário por ID"""
        return self._usuarios.get(id)
    
    def listar_usuarios(self) -> List[Usuario]:
        """Lista todos os usuários"""
        return list(self._usuarios.values())
    
    def atualizar_usuario(self, id: str, nome: Optional[str] = None, idade: Optional[int] = None) -> Optional[Usuario]:
        """Atualiza um usuário"""
        usuario = self._usuarios.get(id)
        if not usuario:
            return None
        
        if nome is not None:
            usuario.nome = nome
        if idade is not None:
            usuario.idade = idade
        
        return usuario
    
    def remover_usuario(self, id: str) -> bool:
        """Remove um usuário e todas suas playlists"""
        if id not in self._usuarios:
            return False
        
        # Remove todas as playlists do usuário
        playlists_para_remover = [p.id for p in self._playlists.values() if p.usuario_id == id]
        for playlist_id in playlists_para_remover:
            del self._playlists[playlist_id]
        
        del self._usuarios[id]
        return True
    
    # ========== MÚSICAS ==========
    
    def criar_musica(self, nome: str, artista: str, id: Optional[str] = None) -> Musica:
        """Cria uma nova música"""
        musica = Musica(
            id=id or gerar_id(),
            nome=nome,
            artista=artista
        )
        self._musicas[musica.id] = musica
        return musica
    
    def obter_musica(self, id: str) -> Optional[Musica]:
        """Obtém uma música por ID"""
        return self._musicas.get(id)
    
    def listar_musicas(self) -> List[Musica]:
        """Lista todas as músicas"""
        return list(self._musicas.values())
    
    def atualizar_musica(self, id: str, nome: Optional[str] = None, artista: Optional[str] = None) -> Optional[Musica]:
        """Atualiza uma música"""
        musica = self._musicas.get(id)
        if not musica:
            return None
        
        if nome is not None:
            musica.nome = nome
        if artista is not None:
            musica.artista = artista
        
        return musica
    
    def remover_musica(self, id: str) -> bool:
        """Remove uma música de todas as playlists"""
        if id not in self._musicas:
            return False
        
        # Remove a música de todas as playlists
        for playlist in self._playlists.values():
            if id in playlist.musicas_ids:
                playlist.musicas_ids.remove(id)
        
        del self._musicas[id]
        return True
    
    # ========== PLAYLISTS ==========
    
    def criar_playlist(self, nome: str, usuario_id: str, musicas_ids: Optional[List[str]] = None, id: Optional[str] = None) -> Playlist:
        """Cria uma nova playlist"""
        # Valida se o usuário existe
        if usuario_id not in self._usuarios:
            raise ValueError('Usuário não encontrado')
        
        # Valida se todas as músicas existem
        if musicas_ids:
            for musica_id in musicas_ids:
                if musica_id not in self._musicas:
                    raise ValueError(f'Música {musica_id} não encontrada')
        
        playlist = Playlist(
            id=id or gerar_id(),
            nome=nome,
            usuario_id=usuario_id,
            musicas_ids=musicas_ids or []
        )
        self._playlists[playlist.id] = playlist
        return playlist
    
    def obter_playlist(self, id: str) -> Optional[Playlist]:
        """Obtém uma playlist por ID"""
        return self._playlists.get(id)
    
    def listar_playlists(self) -> List[Playlist]:
        """Lista todas as playlists"""
        return list(self._playlists.values())
    
    def listar_playlists_por_usuario(self, usuario_id: str) -> List[Playlist]:
        """Lista playlists de um usuário"""
        return [p for p in self._playlists.values() if p.usuario_id == usuario_id]
    
    def listar_musicas_por_playlist(self, playlist_id: str) -> List[Musica]:
        """Lista músicas de uma playlist"""
        playlist = self._playlists.get(playlist_id)
        if not playlist:
            return []
        
        musicas = []
        for musica_id in playlist.musicas_ids:
            musica = self._musicas.get(musica_id)
            if musica:
                musicas.append(musica)
        return musicas
    
    def listar_playlists_por_musica(self, musica_id: str) -> List[Playlist]:
        """Lista playlists que contêm uma música"""
        return [p for p in self._playlists.values() if musica_id in p.musicas_ids]
    
    def atualizar_playlist(self, id: str, nome: Optional[str] = None, usuario_id: Optional[str] = None) -> Optional[Playlist]:
        """Atualiza uma playlist"""
        playlist = self._playlists.get(id)
        if not playlist:
            return None
        
        # Valida usuário se estiver sendo alterado
        if usuario_id is not None:
            if usuario_id not in self._usuarios:
                raise ValueError('Usuário não encontrado')
            playlist.usuario_id = usuario_id
        
        if nome is not None:
            playlist.nome = nome
        
        return playlist
    
    def adicionar_musica_a_playlist(self, playlist_id: str, musica_id: str) -> Optional[Playlist]:
        """Adiciona uma música a uma playlist"""
        playlist = self._playlists.get(playlist_id)
        if not playlist:
            return None
        
        if musica_id not in self._musicas:
            raise ValueError('Música não encontrada')
        
        # Evita duplicatas
        if musica_id not in playlist.musicas_ids:
            playlist.musicas_ids.append(musica_id)
        
        return playlist
    
    def remover_musica_de_playlist(self, playlist_id: str, musica_id: str) -> Optional[Playlist]:
        """Remove uma música de uma playlist"""
        playlist = self._playlists.get(playlist_id)
        if not playlist:
            return None
        
        if musica_id in playlist.musicas_ids:
            playlist.musicas_ids.remove(musica_id)
        
        return playlist
    
    def remover_playlist(self, id: str) -> bool:
        """Remove uma playlist"""
        if id not in self._playlists:
            return False
        
        del self._playlists[id]
        return True


# Instância global compartilhada entre todos os serviços
_repositorio_global = Repositorio()


def get_repositorio() -> Repositorio:
    """Retorna a instância global do repositório"""
    return _repositorio_global
