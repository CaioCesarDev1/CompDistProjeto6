/**
 * Serviço REST implementado com Express - versão Node.js
 */
const express = require('express');
const cors = require('cors');

// Importa o repositório compartilhado
const { getRepositorio } = require('../shared/repository');

const app = express();
app.use(cors());
app.use(express.json());

// Middleware de tratamento de erros global
app.use((err, req, res, next) => {
    console.error('Erro não tratado:', err);
    res.status(500).json({ erro: err.message || 'Erro interno do servidor' });
});

const repo = getRepositorio();

// ========== USUÁRIOS ==========

app.post('/api/usuarios', async (req, res) => {
    try {
        const { nome, idade } = req.body;
        if (!nome || idade === undefined) {
            return res.status(400).json({ erro: 'nome e idade são obrigatórios' });
        }
        
        const usuario = await repo.criarUsuario(nome, idade);
        return res.status(201).json({
            id: usuario.id,
            nome: usuario.nome,
            idade: usuario.idade
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/usuarios', async (req, res) => {
    try {
        const usuarios = await repo.listarUsuarios();
        return res.json(usuarios.map(u => ({
            id: u.id,
            nome: u.nome,
            idade: u.idade
        })));
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/usuarios/:id', async (req, res) => {
    try {
        const usuario = await repo.obterUsuario(req.params.id);
        if (!usuario) {
            return res.status(404).json({ erro: 'Usuário não encontrado' });
        }
        
        return res.json({
            id: usuario.id,
            nome: usuario.nome,
            idade: usuario.idade
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.put('/api/usuarios/:id', async (req, res) => {
    try {
        const { nome, idade } = req.body;
        const usuario = await repo.atualizarUsuario(
            req.params.id,
            nome || null,
            idade !== undefined ? idade : null
        );
        
        if (!usuario) {
            return res.status(404).json({ erro: 'Usuário não encontrado' });
        }
        
        return res.json({
            id: usuario.id,
            nome: usuario.nome,
            idade: usuario.idade
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.delete('/api/usuarios/:id', async (req, res) => {
    try {
        const sucesso = await repo.removerUsuario(req.params.id);
        if (sucesso) {
            return res.status(204).send();
        }
        return res.status(404).json({ erro: 'Usuário não encontrado' });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

// ========== MÚSICAS ==========

app.post('/api/musicas', async (req, res) => {
    try {
        const { nome, artista } = req.body;
        if (!nome || !artista) {
            return res.status(400).json({ erro: 'nome e artista são obrigatórios' });
        }
        
        const musica = await repo.criarMusica(nome, artista);
        return res.status(201).json({
            id: musica.id,
            nome: musica.nome,
            artista: musica.artista
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/musicas', async (req, res) => {
    try {
        const musicas = await repo.listarMusicas();
        return res.json(musicas.map(m => ({
            id: m.id,
            nome: m.nome,
            artista: m.artista
        })));
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/musicas/:id', async (req, res) => {
    try {
        const musica = await repo.obterMusica(req.params.id);
        if (!musica) {
            return res.status(404).json({ erro: 'Música não encontrada' });
        }
        
        return res.json({
            id: musica.id,
            nome: musica.nome,
            artista: musica.artista
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.put('/api/musicas/:id', async (req, res) => {
    try {
        const { nome, artista } = req.body;
        const musica = await repo.atualizarMusica(
            req.params.id,
            nome || null,
            artista || null
        );
        
        if (!musica) {
            return res.status(404).json({ erro: 'Música não encontrada' });
        }
        
        return res.json({
            id: musica.id,
            nome: musica.nome,
            artista: musica.artista
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.delete('/api/musicas/:id', async (req, res) => {
    try {
        const sucesso = await repo.removerMusica(req.params.id);
        if (sucesso) {
            return res.status(204).send();
        }
        return res.status(404).json({ erro: 'Música não encontrada' });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

// ========== PLAYLISTS ==========

app.post('/api/playlists', async (req, res) => {
    try {
        const { nome, usuarioId, musicasIds } = req.body;
        if (!nome || !usuarioId) {
            return res.status(400).json({ erro: 'nome e usuarioId são obrigatórios' });
        }
        
        const playlist = await repo.criarPlaylist(nome, usuarioId, musicasIds || []);
        return res.status(201).json({
            id: playlist.id,
            nome: playlist.nome,
            usuarioId: playlist.usuarioId,
            musicasIds: playlist.musicasIds
        });
    } catch (error) {
        if (error.message.includes('não encontrado')) {
            return res.status(400).json({ erro: error.message });
        }
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/playlists', async (req, res) => {
    try {
        const playlists = await repo.listarPlaylists();
        return res.json(playlists.map(p => ({
            id: p.id,
            nome: p.nome,
            usuarioId: p.usuarioId,
            musicasIds: p.musicasIds
        })));
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/playlists/:id', async (req, res) => {
    try {
        const playlist = await repo.obterPlaylist(req.params.id);
        if (!playlist) {
            return res.status(404).json({ erro: 'Playlist não encontrada' });
        }
        
        return res.json({
            id: playlist.id,
            nome: playlist.nome,
            usuarioId: playlist.usuarioId,
            musicasIds: playlist.musicasIds
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/usuarios/:usuarioId/playlists', async (req, res) => {
    try {
        const playlists = await repo.listarPlaylistsPorUsuario(req.params.usuarioId);
        return res.json(playlists.map(p => ({
            id: p.id,
            nome: p.nome,
            usuarioId: p.usuarioId,
            musicasIds: p.musicasIds
        })));
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/playlists/:id/musicas', async (req, res) => {
    try {
        const musicas = await repo.listarMusicasPorPlaylist(req.params.id);
        return res.json(musicas.map(m => ({
            id: m.id,
            nome: m.nome,
            artista: m.artista
        })));
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.get('/api/musicas/:musicaId/playlists', async (req, res) => {
    try {
        const playlists = await repo.listarPlaylistsPorMusica(req.params.musicaId);
        return res.json(playlists.map(p => ({
            id: p.id,
            nome: p.nome,
            usuarioId: p.usuarioId,
            musicasIds: p.musicasIds
        })));
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.put('/api/playlists/:id', async (req, res) => {
    try {
        const { nome, usuarioId } = req.body;
        const playlist = await repo.atualizarPlaylist(
            req.params.id,
            nome || null,
            usuarioId || null
        );
        
        if (!playlist) {
            return res.status(404).json({ erro: 'Playlist não encontrada' });
        }
        
        return res.json({
            id: playlist.id,
            nome: playlist.nome,
            usuarioId: playlist.usuarioId,
            musicasIds: playlist.musicasIds
        });
    } catch (error) {
        if (error.message.includes('não encontrado')) {
            return res.status(400).json({ erro: error.message });
        }
        return res.status(500).json({ erro: error.message });
    }
});

app.post('/api/playlists/:id/musicas', async (req, res) => {
    try {
        const { musicaId } = req.body;
        if (!musicaId) {
            return res.status(400).json({ erro: 'musicaId é obrigatório' });
        }
        
        const playlist = await repo.adicionarMusicaAPlaylist(req.params.id, musicaId);
        if (!playlist) {
            return res.status(404).json({ erro: 'Playlist não encontrada' });
        }
        
        return res.json({
            id: playlist.id,
            nome: playlist.nome,
            usuarioId: playlist.usuarioId,
            musicasIds: playlist.musicasIds
        });
    } catch (error) {
        if (error.message.includes('não encontrado')) {
            return res.status(400).json({ erro: error.message });
        }
        return res.status(500).json({ erro: error.message });
    }
});

app.delete('/api/playlists/:id/musicas/:musicaId', async (req, res) => {
    try {
        const playlist = await repo.removerMusicaDePlaylist(req.params.id, req.params.musicaId);
        if (!playlist) {
            return res.status(404).json({ erro: 'Playlist não encontrada' });
        }
        
        return res.json({
            id: playlist.id,
            nome: playlist.nome,
            usuarioId: playlist.usuarioId,
            musicasIds: playlist.musicasIds
        });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

app.delete('/api/playlists/:id', async (req, res) => {
    try {
        const sucesso = await repo.removerPlaylist(req.params.id);
        if (sucesso) {
            return res.status(204).send();
        }
        return res.status(404).json({ erro: 'Playlist não encontrada' });
    } catch (error) {
        return res.status(500).json({ erro: error.message });
    }
});

const PORT = 3001;
const server = app.listen(PORT, () => {
    console.log(`🎵 Serviço REST rodando na porta ${PORT}`);
    console.log(`📍 Base URL: http://localhost:${PORT}`);
});

// Remove timeout padrão do servidor - permite que requisições demorem o tempo necessário
// O objetivo é medir o tempo real de resposta, não cortar requisições lentas
server.timeout = 0; // 0 = sem timeout
