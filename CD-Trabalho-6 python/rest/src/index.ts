import express, { Request, Response } from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { repositorio } from '../../shared/models';
import { gerarId } from '../../shared/utils';
import { Usuario, Musica, Playlist } from '../../shared/models';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

// ========== USUÁRIOS ==========

// Criar usuário
app.post('/api/usuarios', (req: Request, res: Response) => {
  try {
    const { nome, idade } = req.body;
    if (!nome || idade === undefined) {
      return res.status(400).json({ erro: 'Nome e idade são obrigatórios' });
    }
    const usuario: Usuario = {
      id: gerarId(),
      nome,
      idade: parseInt(idade)
    };
    const criado = repositorio.criarUsuario(usuario);
    res.status(201).json(criado);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Listar todos os usuários
app.get('/api/usuarios', (req: Request, res: Response) => {
  try {
    const usuarios = repositorio.listarUsuarios();
    res.json(usuarios);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Obter usuário por ID
app.get('/api/usuarios/:id', (req: Request, res: Response) => {
  try {
    const usuario = repositorio.obterUsuario(req.params.id);
    if (!usuario) {
      return res.status(404).json({ erro: 'Usuário não encontrado' });
    }
    res.json(usuario);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Atualizar usuário
app.put('/api/usuarios/:id', (req: Request, res: Response) => {
  try {
    const atualizado = repositorio.atualizarUsuario(req.params.id, req.body);
    if (!atualizado) {
      return res.status(404).json({ erro: 'Usuário não encontrado' });
    }
    res.json(atualizado);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Remover usuário
app.delete('/api/usuarios/:id', (req: Request, res: Response) => {
  try {
    const removido = repositorio.removerUsuario(req.params.id);
    if (!removido) {
      return res.status(404).json({ erro: 'Usuário não encontrado' });
    }
    res.status(204).send();
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// ========== MÚSICAS ==========

// Criar música
app.post('/api/musicas', (req: Request, res: Response) => {
  try {
    const { nome, artista } = req.body;
    if (!nome || !artista) {
      return res.status(400).json({ erro: 'Nome e artista são obrigatórios' });
    }
    const musica: Musica = {
      id: gerarId(),
      nome,
      artista
    };
    const criada = repositorio.criarMusica(musica);
    res.status(201).json(criada);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Listar todas as músicas
app.get('/api/musicas', (req: Request, res: Response) => {
  try {
    const musicas = repositorio.listarMusicas();
    res.json(musicas);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Obter música por ID
app.get('/api/musicas/:id', (req: Request, res: Response) => {
  try {
    const musica = repositorio.obterMusica(req.params.id);
    if (!musica) {
      return res.status(404).json({ erro: 'Música não encontrada' });
    }
    res.json(musica);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Atualizar música
app.put('/api/musicas/:id', (req: Request, res: Response) => {
  try {
    const atualizada = repositorio.atualizarMusica(req.params.id, req.body);
    if (!atualizada) {
      return res.status(404).json({ erro: 'Música não encontrada' });
    }
    res.json(atualizada);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Remover música
app.delete('/api/musicas/:id', (req: Request, res: Response) => {
  try {
    const removida = repositorio.removerMusica(req.params.id);
    if (!removida) {
      return res.status(404).json({ erro: 'Música não encontrada' });
    }
    res.status(204).send();
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// ========== PLAYLISTS ==========

// Criar playlist
app.post('/api/playlists', (req: Request, res: Response) => {
  try {
    const { nome, usuarioId } = req.body;
    if (!nome || !usuarioId) {
      return res.status(400).json({ erro: 'Nome e usuarioId são obrigatórios' });
    }
    const playlist: Playlist = {
      id: gerarId(),
      nome,
      usuarioId,
      musicasIds: []
    };
    const criada = repositorio.criarPlaylist(playlist);
    res.status(201).json(criada);
  } catch (error: any) {
    res.status(400).json({ erro: error.message });
  }
});

// Listar todas as playlists
app.get('/api/playlists', (req: Request, res: Response) => {
  try {
    const playlists = repositorio.listarPlaylists();
    res.json(playlists);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Listar playlists de um usuário
app.get('/api/usuarios/:usuarioId/playlists', (req: Request, res: Response) => {
  try {
    const playlists = repositorio.listarPlaylistsPorUsuario(req.params.usuarioId);
    res.json(playlists);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Obter playlist por ID
app.get('/api/playlists/:id', (req: Request, res: Response) => {
  try {
    const playlist = repositorio.obterPlaylist(req.params.id);
    if (!playlist) {
      return res.status(404).json({ erro: 'Playlist não encontrada' });
    }
    res.json(playlist);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Listar músicas de uma playlist
app.get('/api/playlists/:id/musicas', (req: Request, res: Response) => {
  try {
    const musicas = repositorio.listarMusicasPorPlaylist(req.params.id);
    res.json(musicas);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Listar playlists que contêm uma música
app.get('/api/musicas/:musicaId/playlists', (req: Request, res: Response) => {
  try {
    const playlists = repositorio.listarPlaylistsPorMusica(req.params.musicaId);
    res.json(playlists);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Atualizar playlist
app.put('/api/playlists/:id', (req: Request, res: Response) => {
  try {
    const atualizada = repositorio.atualizarPlaylist(req.params.id, req.body);
    if (!atualizada) {
      return res.status(404).json({ erro: 'Playlist não encontrada' });
    }
    res.json(atualizada);
  } catch (error: any) {
    res.status(400).json({ erro: error.message });
  }
});

// Adicionar música à playlist
app.post('/api/playlists/:id/musicas', (req: Request, res: Response) => {
  try {
    const { musicaId } = req.body;
    if (!musicaId) {
      return res.status(400).json({ erro: 'musicaId é obrigatório' });
    }
    const playlist = repositorio.adicionarMusicaAPlaylist(req.params.id, musicaId);
    if (!playlist) {
      return res.status(404).json({ erro: 'Playlist não encontrada' });
    }
    res.json(playlist);
  } catch (error: any) {
    res.status(400).json({ erro: error.message });
  }
});

// Remover música de playlist
app.delete('/api/playlists/:id/musicas/:musicaId', (req: Request, res: Response) => {
  try {
    const playlist = repositorio.removerMusicaDePlaylist(req.params.id, req.params.musicaId);
    if (!playlist) {
      return res.status(404).json({ erro: 'Playlist não encontrada' });
    }
    res.json(playlist);
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

// Remover playlist
app.delete('/api/playlists/:id', (req: Request, res: Response) => {
  try {
    const removida = repositorio.removerPlaylist(req.params.id);
    if (!removida) {
      return res.status(404).json({ erro: 'Playlist não encontrada' });
    }
    res.status(204).send();
  } catch (error: any) {
    res.status(500).json({ erro: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Serviço REST rodando na porta ${PORT}`);
  console.log(`Acesse: http://localhost:${PORT}`);
});

