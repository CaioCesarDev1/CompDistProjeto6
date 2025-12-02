// Modelos de dados compartilhados entre todas as implementações

export interface Usuario {
  id: string;
  nome: string;
  idade: number;
}

export interface Musica {
  id: string;
  nome: string;
  artista: string;
}

export interface Playlist {
  id: string;
  nome: string;
  usuarioId: string;
  musicasIds: string[];
}

// Repositório em memória compartilhado
export class Repositorio {
  private usuarios: Map<string, Usuario> = new Map();
  private musicas: Map<string, Musica> = new Map();
  private playlists: Map<string, Playlist> = new Map();

  // Usuários
  criarUsuario(usuario: Usuario): Usuario {
    this.usuarios.set(usuario.id, usuario);
    return usuario;
  }

  obterUsuario(id: string): Usuario | undefined {
    return this.usuarios.get(id);
  }

  listarUsuarios(): Usuario[] {
    return Array.from(this.usuarios.values());
  }

  atualizarUsuario(id: string, dados: Partial<Usuario>): Usuario | undefined {
    const usuario = this.usuarios.get(id);
    if (!usuario) return undefined;
    const atualizado = { ...usuario, ...dados };
    this.usuarios.set(id, atualizado);
    return atualizado;
  }

  removerUsuario(id: string): boolean {
    // Remove todas as playlists do usuário
    const playlistsDoUsuario = Array.from(this.playlists.values())
      .filter(p => p.usuarioId === id);
    playlistsDoUsuario.forEach(p => this.playlists.delete(p.id));
    return this.usuarios.delete(id);
  }

  // Músicas
  criarMusica(musica: Musica): Musica {
    this.musicas.set(musica.id, musica);
    return musica;
  }

  obterMusica(id: string): Musica | undefined {
    return this.musicas.get(id);
  }

  listarMusicas(): Musica[] {
    return Array.from(this.musicas.values());
  }

  atualizarMusica(id: string, dados: Partial<Musica>): Musica | undefined {
    const musica = this.musicas.get(id);
    if (!musica) return undefined;
    const atualizado = { ...musica, ...dados };
    this.musicas.set(id, atualizado);
    return atualizado;
  }

  removerMusica(id: string): boolean {
    // Remove a música de todas as playlists
    this.playlists.forEach(playlist => {
      playlist.musicasIds = playlist.musicasIds.filter(mid => mid !== id);
    });
    return this.musicas.delete(id);
  }

  // Playlists
  criarPlaylist(playlist: Playlist): Playlist {
    // Valida se o usuário existe
    if (!this.usuarios.has(playlist.usuarioId)) {
      throw new Error('Usuário não encontrado');
    }
    this.playlists.set(playlist.id, playlist);
    return playlist;
  }

  obterPlaylist(id: string): Playlist | undefined {
    return this.playlists.get(id);
  }

  listarPlaylists(): Playlist[] {
    return Array.from(this.playlists.values());
  }

  listarPlaylistsPorUsuario(usuarioId: string): Playlist[] {
    return Array.from(this.playlists.values())
      .filter(p => p.usuarioId === usuarioId);
  }

  listarMusicasPorPlaylist(playlistId: string): Musica[] {
    const playlist = this.playlists.get(playlistId);
    if (!playlist) return [];
    return playlist.musicasIds
      .map(id => this.musicas.get(id))
      .filter((m): m is Musica => m !== undefined);
  }

  listarPlaylistsPorMusica(musicaId: string): Playlist[] {
    return Array.from(this.playlists.values())
      .filter(p => p.musicasIds.includes(musicaId));
  }

  atualizarPlaylist(id: string, dados: Partial<Playlist>): Playlist | undefined {
    const playlist = this.playlists.get(id);
    if (!playlist) return undefined;
    
    // Valida usuário se estiver sendo alterado
    if (dados.usuarioId && !this.usuarios.has(dados.usuarioId)) {
      throw new Error('Usuário não encontrado');
    }
    
    const atualizado = { ...playlist, ...dados };
    this.playlists.set(id, atualizado);
    return atualizado;
  }

  adicionarMusicaAPlaylist(playlistId: string, musicaId: string): Playlist | undefined {
    const playlist = this.playlists.get(playlistId);
    if (!playlist) return undefined;
    
    // Valida se a música existe
    if (!this.musicas.has(musicaId)) {
      throw new Error('Música não encontrada');
    }
    
    // Evita duplicatas
    if (!playlist.musicasIds.includes(musicaId)) {
      playlist.musicasIds.push(musicaId);
    }
    
    return playlist;
  }

  removerMusicaDePlaylist(playlistId: string, musicaId: string): Playlist | undefined {
    const playlist = this.playlists.get(playlistId);
    if (!playlist) return undefined;
    playlist.musicasIds = playlist.musicasIds.filter(id => id !== musicaId);
    return playlist;
  }

  removerPlaylist(id: string): boolean {
    return this.playlists.delete(id);
  }
}

// Instância singleton do repositório
export const repositorio = new Repositorio();

