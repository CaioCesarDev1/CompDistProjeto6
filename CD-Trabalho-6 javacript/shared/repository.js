/**
 * Repositório usando PostgreSQL - versão Node.js
 */
const { query } = require('./database');
const { Usuario, Musica, Playlist } = require('./models');
const { v4: uuidv4 } = require('uuid');

class Repositorio {
    // ========== USUÁRIOS ==========
    
    async criarUsuario(nome, idade, id = null) {
        const usuarioId = id || uuidv4();
        await query(
            'INSERT INTO usuarios (id, nome, idade) VALUES ($1, $2, $3)',
            [usuarioId, nome, idade]
        );
        return new Usuario(usuarioId, nome, idade);
    }
    
    async obterUsuario(id) {
        const result = await query('SELECT * FROM usuarios WHERE id = $1', [id]);
        if (result.rows.length === 0) {
            return null;
        }
        const row = result.rows[0];
        return new Usuario(row.id, row.nome, row.idade);
    }
    
    async listarUsuarios() {
        const result = await query('SELECT * FROM usuarios ORDER BY nome');
        return result.rows.map(row => new Usuario(row.id, row.nome, row.idade));
    }
    
    async atualizarUsuario(id, nome = null, idade = null) {
        const usuario = await this.obterUsuario(id);
        if (!usuario) {
            return null;
        }
        
        const updates = [];
        const values = [];
        let paramIndex = 1;
        
        if (nome !== null) {
            updates.push(`nome = $${paramIndex++}`);
            values.push(nome);
        }
        if (idade !== null) {
            updates.push(`idade = $${paramIndex++}`);
            values.push(idade);
        }
        
        if (updates.length === 0) {
            return usuario;
        }
        
        values.push(id);
        await query(
            `UPDATE usuarios SET ${updates.join(', ')} WHERE id = $${paramIndex}`,
            values
        );
        
        return await this.obterUsuario(id);
    }
    
    async removerUsuario(id) {
        const result = await query('DELETE FROM usuarios WHERE id = $1', [id]);
        return result.rowCount > 0;
    }
    
    // ========== MÚSICAS ==========
    
    async criarMusica(nome, artista, id = null) {
        const musicaId = id || uuidv4();
        await query(
            'INSERT INTO musicas (id, nome, artista) VALUES ($1, $2, $3)',
            [musicaId, nome, artista]
        );
        return new Musica(musicaId, nome, artista);
    }
    
    async obterMusica(id) {
        const result = await query('SELECT * FROM musicas WHERE id = $1', [id]);
        if (result.rows.length === 0) {
            return null;
        }
        const row = result.rows[0];
        return new Musica(row.id, row.nome, row.artista);
    }
    
    async listarMusicas() {
        const result = await query('SELECT * FROM musicas ORDER BY nome');
        return result.rows.map(row => new Musica(row.id, row.nome, row.artista));
    }
    
    async atualizarMusica(id, nome = null, artista = null) {
        const musica = await this.obterMusica(id);
        if (!musica) {
            return null;
        }
        
        const updates = [];
        const values = [];
        let paramIndex = 1;
        
        if (nome !== null) {
            updates.push(`nome = $${paramIndex++}`);
            values.push(nome);
        }
        if (artista !== null) {
            updates.push(`artista = $${paramIndex++}`);
            values.push(artista);
        }
        
        if (updates.length === 0) {
            return musica;
        }
        
        values.push(id);
        await query(
            `UPDATE musicas SET ${updates.join(', ')} WHERE id = $${paramIndex}`,
            values
        );
        
        return await this.obterMusica(id);
    }
    
    async removerMusica(id) {
        const result = await query('DELETE FROM musicas WHERE id = $1', [id]);
        return result.rowCount > 0;
    }
    
    // ========== PLAYLISTS ==========
    
    async criarPlaylist(nome, usuarioId, musicasIds = [], id = null) {
        // Valida se o usuário existe
        const usuario = await this.obterUsuario(usuarioId);
        if (!usuario) {
            throw new Error('Usuário não encontrado');
        }
        
        const playlistId = id || uuidv4();
        
        // Cria a playlist
        await query(
            'INSERT INTO playlists (id, nome, usuario_id) VALUES ($1, $2, $3)',
            [playlistId, nome, usuarioId]
        );
        
        // Adiciona músicas se fornecidas
        if (musicasIds && musicasIds.length > 0) {
            // Valida se todas as músicas existem
            const placeholders = musicasIds.map((_, i) => `$${i + 1}`).join(',');
            const musicasResult = await query(
                `SELECT id FROM musicas WHERE id IN (${placeholders})`,
                musicasIds
            );
            
            if (musicasResult.rows.length !== musicasIds.length) {
                // Remove a playlist criada
                await query('DELETE FROM playlists WHERE id = $1', [playlistId]);
                throw new Error('Uma ou mais músicas não foram encontradas');
            }
            
            // Insere as associações
            for (const musicaId of musicasIds) {
                await query(
                    'INSERT INTO playlist_musica (playlist_id, musica_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                    [playlistId, musicaId]
                );
            }
        }
        
        return new Playlist(playlistId, nome, usuarioId, musicasIds);
    }
    
    async obterPlaylist(id) {
        const result = await query('SELECT * FROM playlists WHERE id = $1', [id]);
        if (result.rows.length === 0) {
            return null;
        }
        const row = result.rows[0];
        
        // Busca as músicas da playlist
        const musicasResult = await query(
            'SELECT musica_id FROM playlist_musica WHERE playlist_id = $1',
            [id]
        );
        const musicasIds = musicasResult.rows.map(r => r.musica_id);
        
        return new Playlist(row.id, row.nome, row.usuario_id, musicasIds);
    }
    
    async listarPlaylists() {
        try {
            // Otimização: busca todas as playlists e suas músicas em 2 queries ao invés de N+1
            const result = await query('SELECT * FROM playlists ORDER BY nome');
            
            if (result.rows.length === 0) {
                return [];
            }
            
            // Busca todas as associações de uma vez usando IN
            // PostgreSQL tem limite de parâmetros, então processa em lotes se necessário
            const playlistIds = result.rows.map(r => r.id);
            const musicasPorPlaylist = {};
            
            // Processa em lotes de 1000 para evitar limite de parâmetros
            const BATCH_SIZE = 1000;
            for (let i = 0; i < playlistIds.length; i += BATCH_SIZE) {
                const batch = playlistIds.slice(i, i + BATCH_SIZE);
                const placeholders = batch.map((_, idx) => `$${idx + 1}`).join(',');
                const musicasResult = await query(
                    `SELECT playlist_id, musica_id FROM playlist_musica WHERE playlist_id IN (${placeholders})`,
                    batch
                );
                
                // Agrupa músicas por playlist
                for (const row of musicasResult.rows) {
                    if (!musicasPorPlaylist[row.playlist_id]) {
                        musicasPorPlaylist[row.playlist_id] = [];
                    }
                    musicasPorPlaylist[row.playlist_id].push(row.musica_id);
                }
            }
            
            // Cria as playlists com suas músicas
            const playlists = [];
            for (const row of result.rows) {
                const musicasIds = musicasPorPlaylist[row.id] || [];
                playlists.push(new Playlist(row.id, row.nome, row.usuario_id, musicasIds));
            }
            
            return playlists;
        } catch (error) {
            console.error('Erro em listarPlaylists:', error);
            throw error;
        }
    }
    
    async listarPlaylistsPorUsuario(usuarioId) {
        try {
            // Otimização: busca todas as playlists e suas músicas em 2 queries ao invés de N+1
            const result = await query(
                'SELECT * FROM playlists WHERE usuario_id = $1 ORDER BY nome',
                [usuarioId]
            );
            
            if (result.rows.length === 0) {
                return [];
            }
            
            // Busca todas as associações de uma vez usando IN
            const playlistIds = result.rows.map(r => r.id);
            if (playlistIds.length === 0) {
                return result.rows.map(row => new Playlist(row.id, row.nome, row.usuario_id, []));
            }
            
            const placeholders = playlistIds.map((_, i) => `$${i + 1}`).join(',');
            const musicasResult = await query(
                `SELECT playlist_id, musica_id FROM playlist_musica WHERE playlist_id IN (${placeholders})`,
                playlistIds
            );
            
            // Agrupa músicas por playlist
            const musicasPorPlaylist = {};
            for (const row of musicasResult.rows) {
                if (!musicasPorPlaylist[row.playlist_id]) {
                    musicasPorPlaylist[row.playlist_id] = [];
                }
                musicasPorPlaylist[row.playlist_id].push(row.musica_id);
            }
            
            // Cria as playlists com suas músicas
            const playlists = [];
            for (const row of result.rows) {
                const musicasIds = musicasPorPlaylist[row.id] || [];
                playlists.push(new Playlist(row.id, row.nome, row.usuario_id, musicasIds));
            }
            
            return playlists;
        } catch (error) {
            console.error('Erro em listarPlaylistsPorUsuario:', error);
            throw error;
        }
    }
    
    async listarMusicasPorPlaylist(playlistId) {
        const result = await query(
            `SELECT m.* FROM musicas m
             INNER JOIN playlist_musica pm ON m.id = pm.musica_id
             WHERE pm.playlist_id = $1
             ORDER BY m.nome`,
            [playlistId]
        );
        return result.rows.map(row => new Musica(row.id, row.nome, row.artista));
    }
    
    async listarPlaylistsPorMusica(musicaId) {
        try {
            // Otimização: busca todas as playlists e suas músicas em 2 queries ao invés de N+1
            const result = await query(
                `SELECT p.* FROM playlists p
                 INNER JOIN playlist_musica pm ON p.id = pm.playlist_id
                 WHERE pm.musica_id = $1
                 ORDER BY p.nome`,
                [musicaId]
            );
            
            if (result.rows.length === 0) {
                return [];
            }
            
            // Busca todas as associações de uma vez usando IN
            const playlistIds = result.rows.map(r => r.id);
            if (playlistIds.length === 0) {
                return result.rows.map(row => new Playlist(row.id, row.nome, row.usuario_id, []));
            }
            
            const placeholders = playlistIds.map((_, i) => `$${i + 1}`).join(',');
            const musicasResult = await query(
                `SELECT playlist_id, musica_id FROM playlist_musica WHERE playlist_id IN (${placeholders})`,
                playlistIds
            );
            
            // Agrupa músicas por playlist
            const musicasPorPlaylist = {};
            for (const row of musicasResult.rows) {
                if (!musicasPorPlaylist[row.playlist_id]) {
                    musicasPorPlaylist[row.playlist_id] = [];
                }
                musicasPorPlaylist[row.playlist_id].push(row.musica_id);
            }
            
            // Cria as playlists com suas músicas
            const playlists = [];
            for (const row of result.rows) {
                const musicasIds = musicasPorPlaylist[row.id] || [];
                playlists.push(new Playlist(row.id, row.nome, row.usuario_id, musicasIds));
            }
            
            return playlists;
        } catch (error) {
            console.error('Erro em listarPlaylistsPorMusica:', error);
            throw error;
        }
    }
    
    async atualizarPlaylist(id, nome = null, usuarioId = null) {
        const playlist = await this.obterPlaylist(id);
        if (!playlist) {
            return null;
        }
        
        const updates = [];
        const values = [];
        let paramIndex = 1;
        
        if (nome !== null) {
            updates.push(`nome = $${paramIndex++}`);
            values.push(nome);
        }
        if (usuarioId !== null) {
            // Valida se o usuário existe
            const usuario = await this.obterUsuario(usuarioId);
            if (!usuario) {
                throw new Error('Usuário não encontrado');
            }
            updates.push(`usuario_id = $${paramIndex++}`);
            values.push(usuarioId);
        }
        
        if (updates.length === 0) {
            return playlist;
        }
        
        values.push(id);
        await query(
            `UPDATE playlists SET ${updates.join(', ')} WHERE id = $${paramIndex}`,
            values
        );
        
        return await this.obterPlaylist(id);
    }
    
    async adicionarMusicaAPlaylist(playlistId, musicaId) {
        const playlist = await this.obterPlaylist(playlistId);
        if (!playlist) {
            return null;
        }
        
        const musica = await this.obterMusica(musicaId);
        if (!musica) {
            throw new Error('Música não encontrada');
        }
        
        // Evita duplicatas
        if (!playlist.musicasIds.includes(musicaId)) {
            await query(
                'INSERT INTO playlist_musica (playlist_id, musica_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
                [playlistId, musicaId]
            );
        }
        
        return await this.obterPlaylist(playlistId);
    }
    
    async removerMusicaDePlaylist(playlistId, musicaId) {
        const playlist = await this.obterPlaylist(playlistId);
        if (!playlist) {
            return null;
        }
        
        await query(
            'DELETE FROM playlist_musica WHERE playlist_id = $1 AND musica_id = $2',
            [playlistId, musicaId]
        );
        
        return await this.obterPlaylist(playlistId);
    }
    
    async removerPlaylist(id) {
        const result = await query('DELETE FROM playlists WHERE id = $1', [id]);
        return result.rowCount > 0;
    }
}

// Instância global compartilhada entre todos os serviços
const _repositorioGlobal = new Repositorio();

function getRepositorio() {
    return _repositorioGlobal;
}

module.exports = {
    Repositorio,
    getRepositorio
};
