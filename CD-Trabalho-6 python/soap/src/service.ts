import { repositorio } from '../../shared/models';
import { gerarId } from '../../shared/utils';
import { Usuario, Musica, Playlist } from '../../shared/models';

export const service = {
  // ========== USUÁRIOS ==========
  
  criarUsuario: function(args: any, callback: any) {
    try {
      const { nome, idade } = args;
      if (!nome || idade === undefined) {
        return callback({ erro: 'Nome e idade são obrigatórios' });
      }
      const usuario: Usuario = {
        id: gerarId(),
        nome,
        idade: parseInt(idade)
      };
      const criado = repositorio.criarUsuario(usuario);
      callback(null, { usuario: criado });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  obterUsuario: function(args: any, callback: any) {
    try {
      const usuario = repositorio.obterUsuario(args.id);
      if (!usuario) {
        return callback({ erro: 'Usuário não encontrado' });
      }
      callback(null, { usuario });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  listarUsuarios: function(args: any, callback: any) {
    try {
      const usuarios = repositorio.listarUsuarios();
      callback(null, { usuarios: { usuario: usuarios } });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  atualizarUsuario: function(args: any, callback: any) {
    try {
      const atualizado = repositorio.atualizarUsuario(args.id, {
        nome: args.nome,
        idade: args.idade
      });
      if (!atualizado) {
        return callback({ erro: 'Usuário não encontrado' });
      }
      callback(null, { usuario: atualizado });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  removerUsuario: function(args: any, callback: any) {
    try {
      const removido = repositorio.removerUsuario(args.id);
      if (!removido) {
        return callback({ erro: 'Usuário não encontrado' });
      }
      callback(null, { sucesso: true });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  // ========== MÚSICAS ==========

  criarMusica: function(args: any, callback: any) {
    try {
      const { nome, artista } = args;
      if (!nome || !artista) {
        return callback({ erro: 'Nome e artista são obrigatórios' });
      }
      const musica: Musica = {
        id: gerarId(),
        nome,
        artista
      };
      const criada = repositorio.criarMusica(musica);
      callback(null, { musica: criada });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  obterMusica: function(args: any, callback: any) {
    try {
      const musica = repositorio.obterMusica(args.id);
      if (!musica) {
        return callback({ erro: 'Música não encontrada' });
      }
      callback(null, { musica });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  listarMusicas: function(args: any, callback: any) {
    try {
      const musicas = repositorio.listarMusicas();
      callback(null, { musicas: { musica: musicas } });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  atualizarMusica: function(args: any, callback: any) {
    try {
      const atualizada = repositorio.atualizarMusica(args.id, {
        nome: args.nome,
        artista: args.artista
      });
      if (!atualizada) {
        return callback({ erro: 'Música não encontrada' });
      }
      callback(null, { musica: atualizada });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  removerMusica: function(args: any, callback: any) {
    try {
      const removida = repositorio.removerMusica(args.id);
      if (!removida) {
        return callback({ erro: 'Música não encontrada' });
      }
      callback(null, { sucesso: true });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  // ========== PLAYLISTS ==========

  criarPlaylist: function(args: any, callback: any) {
    try {
      const { nome, usuarioId } = args;
      if (!nome || !usuarioId) {
        return callback({ erro: 'Nome e usuarioId são obrigatórios' });
      }
      const playlist: Playlist = {
        id: gerarId(),
        nome,
        usuarioId,
        musicasIds: []
      };
      const criada = repositorio.criarPlaylist(playlist);
      callback(null, { playlist: criada });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  obterPlaylist: function(args: any, callback: any) {
    try {
      const playlist = repositorio.obterPlaylist(args.id);
      if (!playlist) {
        return callback({ erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  listarPlaylists: function(args: any, callback: any) {
    try {
      const playlists = repositorio.listarPlaylists();
      callback(null, { playlists: { playlist: playlists } });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  listarPlaylistsPorUsuario: function(args: any, callback: any) {
    try {
      const playlists = repositorio.listarPlaylistsPorUsuario(args.usuarioId);
      callback(null, { playlists: { playlist: playlists } });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  listarMusicasPorPlaylist: function(args: any, callback: any) {
    try {
      const musicas = repositorio.listarMusicasPorPlaylist(args.playlistId);
      callback(null, { musicas: { musica: musicas } });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  listarPlaylistsPorMusica: function(args: any, callback: any) {
    try {
      const playlists = repositorio.listarPlaylistsPorMusica(args.musicaId);
      callback(null, { playlists: { playlist: playlists } });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  atualizarPlaylist: function(args: any, callback: any) {
    try {
      const atualizada = repositorio.atualizarPlaylist(args.id, {
        nome: args.nome,
        usuarioId: args.usuarioId
      });
      if (!atualizada) {
        return callback({ erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist: atualizada });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  adicionarMusicaAPlaylist: function(args: any, callback: any) {
    try {
      const playlist = repositorio.adicionarMusicaAPlaylist(args.playlistId, args.musicaId);
      if (!playlist) {
        return callback({ erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  removerMusicaDePlaylist: function(args: any, callback: any) {
    try {
      const playlist = repositorio.removerMusicaDePlaylist(args.playlistId, args.musicaId);
      if (!playlist) {
        return callback({ erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  },

  removerPlaylist: function(args: any, callback: any) {
    try {
      const removida = repositorio.removerPlaylist(args.id);
      if (!removida) {
        return callback({ erro: 'Playlist não encontrada' });
      }
      callback(null, { sucesso: true });
    } catch (error: any) {
      callback({ erro: error.message });
    }
  }
};

