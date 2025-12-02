import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import { repositorio, Usuario, Musica, Playlist } from '../../shared/models';
import { gerarId } from '../../shared/utils';
import { join } from 'path';

// Ajustar caminho do proto
// Em dev (ts-node): __dirname = src/, proto está em ../proto/
// Em build: __dirname = dist/src/, proto está em ../../proto/ (volta para grpc/proto/)
const isDev = !__dirname.includes('dist');
const PROTO_PATH = isDev 
  ? join(__dirname, '../proto/streaming.proto')
  : join(__dirname, '../../proto/streaming.proto');

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const streamingProto = grpc.loadPackageDefinition(packageDefinition).streaming as any;

const PORT = '0.0.0.0:3004';

const server = new grpc.Server();

// Implementação dos métodos
server.addService(streamingProto.StreamingMusicasService.service, {
  // ========== USUÁRIOS ==========
  
  criarUsuario: (call: any, callback: any) => {
    try {
      const { nome, idade } = call.request;
      if (!nome || idade === undefined) {
        return callback(null, { erro: 'Nome e idade são obrigatórios' });
      }
      const usuario: Usuario = {
        id: gerarId(),
        nome,
        idade
      };
      const criado = repositorio.criarUsuario(usuario);
      callback(null, { usuario: criado });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  obterUsuario: (call: any, callback: any) => {
    try {
      const usuario = repositorio.obterUsuario(call.request.id);
      if (!usuario) {
        return callback(null, { erro: 'Usuário não encontrado' });
      }
      callback(null, { usuario });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  listarUsuarios: (call: any, callback: any) => {
    try {
      const usuarios = repositorio.listarUsuarios();
      callback(null, { usuarios });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  atualizarUsuario: (call: any, callback: any) => {
    try {
      const { id, nome, idade } = call.request;
      const dados: any = {};
      if (nome && nome !== '') dados.nome = nome;
      if (idade !== undefined && idade !== 0) dados.idade = idade;
      const atualizado = repositorio.atualizarUsuario(id, dados);
      if (!atualizado) {
        return callback(null, { erro: 'Usuário não encontrado' });
      }
      callback(null, { usuario: atualizado });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  removerUsuario: (call: any, callback: any) => {
    try {
      const removido = repositorio.removerUsuario(call.request.id);
      callback(null, { sucesso: removido });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  // ========== MÚSICAS ==========

  criarMusica: (call: any, callback: any) => {
    try {
      const { nome, artista } = call.request;
      if (!nome || !artista) {
        return callback(null, { erro: 'Nome e artista são obrigatórios' });
      }
      const musica: Musica = {
        id: gerarId(),
        nome,
        artista
      };
      const criada = repositorio.criarMusica(musica);
      callback(null, { musica: criada });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  obterMusica: (call: any, callback: any) => {
    try {
      const musica = repositorio.obterMusica(call.request.id);
      if (!musica) {
        return callback(null, { erro: 'Música não encontrada' });
      }
      callback(null, { musica });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  listarMusicas: (call: any, callback: any) => {
    try {
      const musicas = repositorio.listarMusicas();
      callback(null, { musicas });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  atualizarMusica: (call: any, callback: any) => {
    try {
      const { id, nome, artista } = call.request;
      const dados: any = {};
      if (nome && nome !== '') dados.nome = nome;
      if (artista && artista !== '') dados.artista = artista;
      const atualizada = repositorio.atualizarMusica(id, dados);
      if (!atualizada) {
        return callback(null, { erro: 'Música não encontrada' });
      }
      callback(null, { musica: atualizada });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  removerMusica: (call: any, callback: any) => {
    try {
      const removida = repositorio.removerMusica(call.request.id);
      callback(null, { sucesso: removida });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  // ========== PLAYLISTS ==========

  criarPlaylist: (call: any, callback: any) => {
    try {
      const { nome, usuarioId } = call.request;
      if (!nome || !usuarioId) {
        return callback(null, { erro: 'Nome e usuarioId são obrigatórios' });
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
      callback(null, { erro: error.message });
    }
  },

  obterPlaylist: (call: any, callback: any) => {
    try {
      const playlist = repositorio.obterPlaylist(call.request.id);
      if (!playlist) {
        return callback(null, { erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  listarPlaylists: (call: any, callback: any) => {
    try {
      const playlists = repositorio.listarPlaylists();
      callback(null, { playlists });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  listarPlaylistsPorUsuario: (call: any, callback: any) => {
    try {
      const playlists = repositorio.listarPlaylistsPorUsuario(call.request.usuarioId);
      callback(null, { playlists });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  listarMusicasPorPlaylist: (call: any, callback: any) => {
    try {
      const musicas = repositorio.listarMusicasPorPlaylist(call.request.playlistId);
      callback(null, { musicas });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  listarPlaylistsPorMusica: (call: any, callback: any) => {
    try {
      const playlists = repositorio.listarPlaylistsPorMusica(call.request.musicaId);
      callback(null, { playlists });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  atualizarPlaylist: (call: any, callback: any) => {
    try {
      const { id, nome, usuarioId } = call.request;
      const dados: any = {};
      if (nome && nome !== '') dados.nome = nome;
      if (usuarioId && usuarioId !== '') dados.usuarioId = usuarioId;
      const atualizada = repositorio.atualizarPlaylist(id, dados);
      if (!atualizada) {
        return callback(null, { erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist: atualizada });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  adicionarMusicaAPlaylist: (call: any, callback: any) => {
    try {
      const { playlistId, musicaId } = call.request;
      const playlist = repositorio.adicionarMusicaAPlaylist(playlistId, musicaId);
      if (!playlist) {
        return callback(null, { erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  removerMusicaDePlaylist: (call: any, callback: any) => {
    try {
      const { playlistId, musicaId } = call.request;
      const playlist = repositorio.removerMusicaDePlaylist(playlistId, musicaId);
      if (!playlist) {
        return callback(null, { erro: 'Playlist não encontrada' });
      }
      callback(null, { playlist });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  },

  removerPlaylist: (call: any, callback: any) => {
    try {
      const removida = repositorio.removerPlaylist(call.request.id);
      callback(null, { sucesso: removida });
    } catch (error: any) {
      callback(null, { erro: error.message });
    }
  }
});

server.bindAsync(PORT, grpc.ServerCredentials.createInsecure(), (error, port) => {
  if (error) {
    if (error.message.includes('EADDRINUSE')) {
      console.error(`Erro: A porta ${PORT} já está em uso.`);
      console.error('Por favor, pare o processo que está usando essa porta ou use outra porta.');
      console.error('No Windows, você pode usar: netstat -ano | findstr :3004');
    } else {
      console.error('Erro ao iniciar servidor gRPC:', error);
    }
    process.exit(1);
    return;
  }
  // server.start() não é mais necessário nas versões recentes do @grpc/grpc-js
  console.log(`Serviço gRPC rodando na porta ${port}`);
  console.log(`Endpoint: ${PORT}`);
});

