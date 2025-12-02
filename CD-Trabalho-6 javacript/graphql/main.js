/**
 * Serviço GraphQL implementado com Express e express-graphql - versão Node.js
 */
const express = require('express');
const cors = require('cors');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema } = require('graphql');

// Importa o repositório compartilhado
const { getRepositorio } = require('../shared/repository');

const app = express();
app.use(cors());
app.use(express.json());

// Middleware de tratamento de erros global
app.use((err, req, res, next) => {
    console.error('Erro não tratado:', err);
    res.status(500).json({ errors: [{ message: err.message || 'Erro interno do servidor' }] });
});

const repo = getRepositorio();

// Schema GraphQL
const schema = buildSchema(`
    type Usuario {
        id: String!
        nome: String!
        idade: Int!
    }
    
    type Musica {
        id: String!
        nome: String!
        artista: String!
    }
    
    type Playlist {
        id: String!
        nome: String!
        usuarioId: String!
        musicasIds: [String!]!
    }
    
    input UsuarioInput {
        nome: String!
        idade: Int!
    }
    
    input MusicaInput {
        nome: String!
        artista: String!
    }
    
    input PlaylistInput {
        nome: String!
        usuarioId: String!
    }
    
    type Query {
        usuario(id: String!): Usuario
        usuarios: [Usuario!]!
        musica(id: String!): Musica
        musicas: [Musica!]!
        playlist(id: String!): Playlist
        playlists: [Playlist!]!
        playlistsPorUsuario(usuarioId: String!): [Playlist!]!
        musicasPorPlaylist(playlistId: String!): [Musica!]!
        playlistsPorMusica(musicaId: String!): [Playlist!]!
    }
    
    type Mutation {
        criarUsuario(input: UsuarioInput!): Usuario!
        atualizarUsuario(id: String!, nome: String, idade: Int): Usuario
        removerUsuario(id: String!): Boolean!
        criarMusica(input: MusicaInput!): Musica!
        atualizarMusica(id: String!, nome: String, artista: String): Musica
        removerMusica(id: String!): Boolean!
        criarPlaylist(input: PlaylistInput!): Playlist!
        atualizarPlaylist(id: String!, nome: String, usuarioId: String): Playlist
        adicionarMusicaAPlaylist(playlistId: String!, musicaId: String!): Playlist
        removerMusicaDePlaylist(playlistId: String!, musicaId: String!): Playlist
        removerPlaylist(id: String!): Boolean!
    }
`);

// Root resolver
const root = {
    // ========== QUERIES ==========
    
    usuario: async ({ id }) => {
        return await repo.obterUsuario(id);
    },
    
    usuarios: async () => {
        return await repo.listarUsuarios();
    },
    
    musica: async ({ id }) => {
        return await repo.obterMusica(id);
    },
    
    musicas: async () => {
        return await repo.listarMusicas();
    },
    
    playlist: async ({ id }) => {
        return await repo.obterPlaylist(id);
    },
    
    playlists: async () => {
        return await repo.listarPlaylists();
    },
    
    playlistsPorUsuario: async ({ usuarioId }) => {
        return await repo.listarPlaylistsPorUsuario(usuarioId);
    },
    
    musicasPorPlaylist: async ({ playlistId }) => {
        return await repo.listarMusicasPorPlaylist(playlistId);
    },
    
    playlistsPorMusica: async ({ musicaId }) => {
        return await repo.listarPlaylistsPorMusica(musicaId);
    },
    
    // ========== MUTATIONS ==========
    
    criarUsuario: async ({ input }) => {
        return await repo.criarUsuario(input.nome, input.idade);
    },
    
    atualizarUsuario: async ({ id, nome, idade }) => {
        return await repo.atualizarUsuario(id, nome || null, idade !== undefined ? idade : null);
    },
    
    removerUsuario: async ({ id }) => {
        return await repo.removerUsuario(id);
    },
    
    criarMusica: async ({ input }) => {
        return await repo.criarMusica(input.nome, input.artista);
    },
    
    atualizarMusica: async ({ id, nome, artista }) => {
        return await repo.atualizarMusica(id, nome || null, artista || null);
    },
    
    removerMusica: async ({ id }) => {
        return await repo.removerMusica(id);
    },
    
    criarPlaylist: async ({ input }) => {
        try {
            return await repo.criarPlaylist(input.nome, input.usuarioId);
        } catch (error) {
            throw new Error(error.message);
        }
    },
    
    atualizarPlaylist: async ({ id, nome, usuarioId }) => {
        try {
            return await repo.atualizarPlaylist(id, nome || null, usuarioId || null);
        } catch (error) {
            throw new Error(error.message);
        }
    },
    
    adicionarMusicaAPlaylist: async ({ playlistId, musicaId }) => {
        try {
            const playlist = await repo.adicionarMusicaAPlaylist(playlistId, musicaId);
            if (!playlist) {
                throw new Error('Playlist não encontrada');
            }
            return playlist;
        } catch (error) {
            throw new Error(error.message);
        }
    },
    
    removerMusicaDePlaylist: async ({ playlistId, musicaId }) => {
        const playlist = await repo.removerMusicaDePlaylist(playlistId, musicaId);
        if (!playlist) {
            throw new Error('Playlist não encontrada');
        }
        return playlist;
    },
    
    removerPlaylist: async ({ id }) => {
        return await repo.removerPlaylist(id);
    }
};

// Middleware GraphQL
app.use('/graphql', graphqlHTTP({
    schema: schema,
    rootValue: root,
    graphiql: false, // Desabilita GraphiQL para manter compatibilidade
    customFormatErrorFn: (error) => {
        return {
            message: error.message,
            locations: error.locations,
            path: error.path
        };
    }
}));

// Endpoint GET para compatibilidade com testes Locust
app.get('/graphql', (req, res) => {
    const query = req.query.query;
    const variables = req.query.variables ? JSON.parse(req.query.variables) : {};
    
    if (!query) {
        return res.status(400).json({ errors: [{ message: 'Query não fornecida. Use ?query=...' }] });
    }
    
    const { graphql } = require('graphql');
    
    graphql(schema, query, root, null, variables)
        .then(result => {
            if (result.errors) {
                return res.status(400).json({ errors: result.errors.map(e => ({ message: e.message })) });
            }
            return res.json({ data: result.data });
        })
        .catch(error => {
            return res.status(500).json({ errors: [{ message: error.message }] });
        });
});

const PORT = 3003;
const server = app.listen(PORT, () => {
    console.log(`🎵 Serviço GraphQL rodando na porta ${PORT}`);
    console.log(`📍 Endpoint: http://localhost:${PORT}/graphql`);
});

// Remove timeout padrão do servidor - permite que requisições demorem o tempo necessário
// O objetivo é medir o tempo real de resposta, não cortar requisições lentas
server.timeout = 0; // 0 = sem timeout

