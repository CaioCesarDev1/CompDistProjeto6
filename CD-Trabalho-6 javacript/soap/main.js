/**
 * Serviço SOAP implementado com Express - versão Node.js
 */
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const xml2js = require('xml2js');

// Importa o repositório compartilhado
const { getRepositorio } = require('../shared/repository');

const app = express();
app.use(cors());
app.use(express.text({ type: 'text/xml' }));

const repo = getRepositorio();

// Namespace SOAP
const SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/';
const TNS_NS = 'http://streaming-musicas.com/soap';

const builder = new xml2js.Builder({
    xmldec: { version: '1.0', encoding: 'UTF-8' },
    renderOpts: { pretty: true, indent: '  ' }
});

function criarRespostaSOAP(bodyContent) {
    return {
        'soap:Envelope': {
            $: {
                'xmlns:soap': SOAP_NS,
                'xmlns:tns': TNS_NS
            },
            'soap:Body': [bodyContent]
        }
    };
}

function criarRespostaErro(mensagem) {
    return {
        'soap:Envelope': {
            $: {
                'xmlns:soap': SOAP_NS
            },
            'soap:Body': [{
                'soap:Fault': [{
                    'faultstring': [mensagem]
                }]
            }]
        }
    };
}

// Middleware de tratamento de erros global (deve vir depois das definições)
app.use((err, req, res, next) => {
    console.error('Erro não tratado:', err);
    const erro = criarRespostaErro(err.message || 'Erro interno do servidor');
    res.setHeader('Content-Type', 'text/xml');
    res.status(500).send(builder.buildObject(erro));
});

app.get('/wsdl', (req, res) => {
    try {
        const wsdlPath = path.join(__dirname, 'wsdl.wsdl');
        if (fs.existsSync(wsdlPath)) {
            const wsdlContent = fs.readFileSync(wsdlPath, 'utf-8');
            res.setHeader('Content-Type', 'text/xml');
            return res.send(wsdlContent);
        } else {
            return res.status(404).send('WSDL não encontrado');
        }
    } catch (error) {
        return res.status(500).send(`Erro ao carregar WSDL: ${error.message}`);
    }
});

app.post('/soap', async (req, res) => {
    try {
        const xmlString = req.body;
        const parser = new xml2js.Parser();
        
        parser.parseString(xmlString, (err, result) => {
            if (err) {
                const erro = criarRespostaErro(`Erro ao parsear XML: ${err.message}`);
                res.setHeader('Content-Type', 'text/xml');
                return res.status(500).send(builder.buildObject(erro));
            }
            
            try {
                const envelope = result['soap:Envelope'] || result['soapenv:Envelope'];
                if (!envelope) {
                    const erro = criarRespostaErro('Envelope SOAP não encontrado');
                    res.setHeader('Content-Type', 'text/xml');
                    return res.status(500).send(builder.buildObject(erro));
                }
                
                const body = envelope['soap:Body'] || envelope['soapenv:Body'];
                if (!body || !body[0]) {
                    const erro = criarRespostaErro('Body SOAP não encontrado');
                    res.setHeader('Content-Type', 'text/xml');
                    return res.status(500).send(builder.buildObject(erro));
                }
                
                // Pega o primeiro elemento filho (a operação)
                const operacaoObj = body[0];
                const operacaoKeys = Object.keys(operacaoObj).filter(k => !k.startsWith('$'));
                if (operacaoKeys.length === 0) {
                    const erro = criarRespostaErro('Operação não encontrada');
                    res.setHeader('Content-Type', 'text/xml');
                    return res.status(500).send(builder.buildObject(erro));
                }
                
                const nomeOperacao = operacaoKeys[0].replace(/^tns:/, '').replace(/^ns1:/, '');
                const operacao = operacaoObj[operacaoKeys[0]];
                
                // Chama a função correspondente
                if (handlers[nomeOperacao]) {
                    handlers[nomeOperacao](operacao)
                        .then(resposta => {
                            res.setHeader('Content-Type', 'text/xml');
                            return res.send(builder.buildObject(resposta));
                        })
                        .catch(error => {
                            const erro = criarRespostaErro(`Erro: ${error.message}`);
                            res.setHeader('Content-Type', 'text/xml');
                            return res.status(500).send(builder.buildObject(erro));
                        });
                    return;
                } else {
                    const erro = criarRespostaErro(`Operação ${nomeOperacao} não encontrada`);
                    res.setHeader('Content-Type', 'text/xml');
                    return res.status(500).send(builder.buildObject(erro));
                }
            } catch (error) {
                const erro = criarRespostaErro(`Erro: ${error.message}`);
                res.setHeader('Content-Type', 'text/xml');
                return res.status(500).send(builder.buildObject(erro));
            }
        });
    } catch (error) {
        const erro = criarRespostaErro(`Erro: ${error.message}`);
        res.setHeader('Content-Type', 'text/xml');
        return res.status(500).send(builder.buildObject(erro));
    }
});

// Endpoints GET para facilitar testes (retornam JSON)
app.get('/api/usuarios', async (req, res) => {
    try {
        const usuarios = await repo.listarUsuarios();
        return res.json({ usuarios: usuarios.map(u => ({
            usuario: {
                id: u.id,
                nome: u.nome,
                idade: u.idade
            }
        })) });
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
});

app.get('/api/musicas', async (req, res) => {
    try {
        const musicas = await repo.listarMusicas();
        return res.json({ musicas: musicas.map(m => ({
            musica: {
                id: m.id,
                nome: m.nome,
                artista: m.artista
            }
        })) });
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
});

app.get('/api/playlists', async (req, res) => {
    try {
        const playlists = await repo.listarPlaylists();
        return res.json({ playlists: playlists.map(p => ({
            playlist: {
                id: p.id,
                nome: p.nome,
                usuarioId: p.usuarioId,
                musicasIds: p.musicasIds
            }
        })) });
    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
});

// Handlers para cada operação SOAP
function getElementValue(obj, key) {
    if (!obj || !obj[key]) {
        return null;
    }
    const value = obj[key][0];
    if (typeof value === 'string') {
        return value;
    }
    if (typeof value === 'object' && value._) {
        return value._;
    }
    return value;
}

async function handlerCriarUsuario(operacao) {
    const nome = getElementValue(operacao, 'nome');
    const idade = getElementValue(operacao, 'idade');
    
    if (!nome || !idade) {
        return criarRespostaErro('Nome e idade são obrigatórios');
    }
    
    try {
        const usuario = await repo.criarUsuario(nome, parseInt(idade));
        
        return criarRespostaSOAP({
            [`tns:criarUsuarioResponse`]: [{
                usuario: [{
                    id: [usuario.id],
                    nome: [usuario.nome],
                    idade: [usuario.idade.toString()]
                }]
            }]
        });
    } catch (error) {
        return criarRespostaErro(error.message);
    }
}

async function handlerObterUsuario(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const usuario = await repo.obterUsuario(id);
    if (!usuario) {
        return criarRespostaErro('Usuário não encontrado');
    }
    
    return criarRespostaSOAP({
        [`tns:obterUsuarioResponse`]: [{
            usuario: [{
                id: [usuario.id],
                nome: [usuario.nome],
                idade: [usuario.idade.toString()]
            }]
        }]
    });
}

async function handlerListarUsuarios(operacao) {
    const usuarios = await repo.listarUsuarios();
    
    return criarRespostaSOAP({
        [`tns:listarUsuariosResponse`]: [{
            usuarios: [{
                usuario: usuarios.map(u => ({
                    id: [u.id],
                    nome: [u.nome],
                    idade: [u.idade.toString()]
                }))
            }]
        }]
    });
}

async function handlerAtualizarUsuario(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const nome = getElementValue(operacao, 'nome');
    const idade = getElementValue(operacao, 'idade');
    
    const usuario = await repo.atualizarUsuario(
        id,
        nome || null,
        idade ? parseInt(idade) : null
    );
    
    if (!usuario) {
        return criarRespostaErro('Usuário não encontrado');
    }
    
    return criarRespostaSOAP({
        [`tns:atualizarUsuarioResponse`]: [{
            usuario: [{
                id: [usuario.id],
                nome: [usuario.nome],
                idade: [usuario.idade.toString()]
            }]
        }]
    });
}

async function handlerRemoverUsuario(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const sucesso = await repo.removerUsuario(id);
    if (!sucesso) {
        return criarRespostaErro('Usuário não encontrado');
    }
    
    return criarRespostaSOAP({
        [`tns:removerUsuarioResponse`]: [{
            sucesso: ['true']
        }]
    });
}

async function handlerCriarMusica(operacao) {
    const nome = getElementValue(operacao, 'nome');
    const artista = getElementValue(operacao, 'artista');
    
    if (!nome || !artista) {
        return criarRespostaErro('Nome e artista são obrigatórios');
    }
    
    try {
        const musica = await repo.criarMusica(nome, artista);
        
        return criarRespostaSOAP({
            [`tns:criarMusicaResponse`]: [{
                musica: [{
                    id: [musica.id],
                    nome: [musica.nome],
                    artista: [musica.artista]
                }]
            }]
        });
    } catch (error) {
        return criarRespostaErro(error.message);
    }
}

async function handlerObterMusica(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const musica = await repo.obterMusica(id);
    if (!musica) {
        return criarRespostaErro('Música não encontrada');
    }
    
    return criarRespostaSOAP({
        [`tns:obterMusicaResponse`]: [{
            musica: [{
                id: [musica.id],
                nome: [musica.nome],
                artista: [musica.artista]
            }]
        }]
    });
}

async function handlerListarMusicas(operacao) {
    const musicas = await repo.listarMusicas();
    
    return criarRespostaSOAP({
        [`tns:listarMusicasResponse`]: [{
            musicas: [{
                musica: musicas.map(m => ({
                    id: [m.id],
                    nome: [m.nome],
                    artista: [m.artista]
                }))
            }]
        }]
    });
}

async function handlerAtualizarMusica(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const nome = getElementValue(operacao, 'nome');
    const artista = getElementValue(operacao, 'artista');
    
    const musica = await repo.atualizarMusica(id, nome || null, artista || null);
    if (!musica) {
        return criarRespostaErro('Música não encontrada');
    }
    
    return criarRespostaSOAP({
        [`tns:atualizarMusicaResponse`]: [{
            musica: [{
                id: [musica.id],
                nome: [musica.nome],
                artista: [musica.artista]
            }]
        }]
    });
}

async function handlerRemoverMusica(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const sucesso = await repo.removerMusica(id);
    if (!sucesso) {
        return criarRespostaErro('Música não encontrada');
    }
    
    return criarRespostaSOAP({
        [`tns:removerMusicaResponse`]: [{
            sucesso: ['true']
        }]
    });
}

async function handlerCriarPlaylist(operacao) {
    const nome = getElementValue(operacao, 'nome');
    const usuarioId = getElementValue(operacao, 'usuarioId');
    
    if (!nome || !usuarioId) {
        return criarRespostaErro('Nome e usuarioId são obrigatórios');
    }
    
    try {
        const playlist = await repo.criarPlaylist(nome, usuarioId);
        
        return criarRespostaSOAP({
            [`tns:criarPlaylistResponse`]: [{
                playlist: [{
                    id: [playlist.id],
                    nome: [playlist.nome],
                    usuarioId: [playlist.usuarioId],
                    musicasIds: [{
                        item: playlist.musicasIds
                    }]
                }]
            }]
        });
    } catch (error) {
        return criarRespostaErro(error.message);
    }
}

async function handlerObterPlaylist(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const playlist = await repo.obterPlaylist(id);
    if (!playlist) {
        return criarRespostaErro('Playlist não encontrada');
    }
    
    return criarRespostaSOAP({
        [`tns:obterPlaylistResponse`]: [{
            playlist: [{
                id: [playlist.id],
                nome: [playlist.nome],
                usuarioId: [playlist.usuarioId],
                musicasIds: [{
                    item: playlist.musicasIds
                }]
            }]
        }]
    });
}

async function handlerListarPlaylists(operacao) {
    const playlists = await repo.listarPlaylists();
    
    return criarRespostaSOAP({
        [`tns:listarPlaylistsResponse`]: [{
            playlists: [{
                playlist: playlists.map(p => ({
                    id: [p.id],
                    nome: [p.nome],
                    usuarioId: [p.usuarioId],
                    musicasIds: [{
                        item: p.musicasIds
                    }]
                }))
            }]
        }]
    });
}

async function handlerListarPlaylistsPorUsuario(operacao) {
    const usuarioId = getElementValue(operacao, 'usuarioId');
    if (!usuarioId) {
        return criarRespostaErro('usuarioId é obrigatório');
    }
    
    const playlists = await repo.listarPlaylistsPorUsuario(usuarioId);
    
    return criarRespostaSOAP({
        [`tns:listarPlaylistsPorUsuarioResponse`]: [{
            playlists: [{
                playlist: playlists.map(p => ({
                    id: [p.id],
                    nome: [p.nome],
                    usuarioId: [p.usuarioId],
                    musicasIds: [{
                        item: p.musicasIds
                    }]
                }))
            }]
        }]
    });
}

async function handlerListarMusicasPorPlaylist(operacao) {
    const playlistId = getElementValue(operacao, 'playlistId');
    if (!playlistId) {
        return criarRespostaErro('playlistId é obrigatório');
    }
    
    const musicas = await repo.listarMusicasPorPlaylist(playlistId);
    
    return criarRespostaSOAP({
        [`tns:listarMusicasPorPlaylistResponse`]: [{
            musicas: [{
                musica: musicas.map(m => ({
                    id: [m.id],
                    nome: [m.nome],
                    artista: [m.artista]
                }))
            }]
        }]
    });
}

async function handlerListarPlaylistsPorMusica(operacao) {
    const musicaId = getElementValue(operacao, 'musicaId');
    if (!musicaId) {
        return criarRespostaErro('musicaId é obrigatório');
    }
    
    const playlists = await repo.listarPlaylistsPorMusica(musicaId);
    
    return criarRespostaSOAP({
        [`tns:listarPlaylistsPorMusicaResponse`]: [{
            playlists: [{
                playlist: playlists.map(p => ({
                    id: [p.id],
                    nome: [p.nome],
                    usuarioId: [p.usuarioId],
                    musicasIds: [{
                        item: p.musicasIds
                    }]
                }))
            }]
        }]
    });
}

async function handlerAtualizarPlaylist(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const nome = getElementValue(operacao, 'nome');
    const usuarioId = getElementValue(operacao, 'usuarioId');
    
    try {
        const playlist = await repo.atualizarPlaylist(
            id,
            nome || null,
            usuarioId || null
        );
        
        if (!playlist) {
            return criarRespostaErro('Playlist não encontrada');
        }
        
        return criarRespostaSOAP({
            [`tns:atualizarPlaylistResponse`]: [{
                playlist: [{
                    id: [playlist.id],
                    nome: [playlist.nome],
                    usuarioId: [playlist.usuarioId],
                    musicasIds: [{
                        item: playlist.musicasIds
                    }]
                }]
            }]
        });
    } catch (error) {
        return criarRespostaErro(error.message);
    }
}

async function handlerAdicionarMusicaAPlaylist(operacao) {
    const playlistId = getElementValue(operacao, 'playlistId');
    const musicaId = getElementValue(operacao, 'musicaId');
    
    if (!playlistId || !musicaId) {
        return criarRespostaErro('playlistId e musicaId são obrigatórios');
    }
    
    try {
        const playlist = await repo.adicionarMusicaAPlaylist(playlistId, musicaId);
        if (!playlist) {
            return criarRespostaErro('Playlist não encontrada');
        }
        
        return criarRespostaSOAP({
            [`tns:adicionarMusicaAPlaylistResponse`]: [{
                playlist: [{
                    id: [playlist.id],
                    nome: [playlist.nome],
                    usuarioId: [playlist.usuarioId],
                    musicasIds: [{
                        item: playlist.musicasIds
                    }]
                }]
            }]
        });
    } catch (error) {
        return criarRespostaErro(error.message);
    }
}

async function handlerRemoverMusicaDePlaylist(operacao) {
    const playlistId = getElementValue(operacao, 'playlistId');
    const musicaId = getElementValue(operacao, 'musicaId');
    
    if (!playlistId || !musicaId) {
        return criarRespostaErro('playlistId e musicaId são obrigatórios');
    }
    
    const playlist = await repo.removerMusicaDePlaylist(playlistId, musicaId);
    if (!playlist) {
        return criarRespostaErro('Playlist não encontrada');
    }
    
    return criarRespostaSOAP({
        [`tns:removerMusicaDePlaylistResponse`]: [{
            playlist: [{
                id: [playlist.id],
                nome: [playlist.nome],
                usuarioId: [playlist.usuarioId],
                musicasIds: [{
                    item: playlist.musicasIds
                }]
            }]
        }]
    });
}

async function handlerRemoverPlaylist(operacao) {
    const id = getElementValue(operacao, 'id');
    if (!id) {
        return criarRespostaErro('ID é obrigatório');
    }
    
    const sucesso = await repo.removerPlaylist(id);
    if (!sucesso) {
        return criarRespostaErro('Playlist não encontrada');
    }
    
    return criarRespostaSOAP({
        [`tns:removerPlaylistResponse`]: [{
            sucesso: ['true']
        }]
    });
}

// Mapeamento de operações para handlers
const handlers = {
    'criarUsuario': handlerCriarUsuario,
    'obterUsuario': handlerObterUsuario,
    'listarUsuarios': handlerListarUsuarios,
    'atualizarUsuario': handlerAtualizarUsuario,
    'removerUsuario': handlerRemoverUsuario,
    'criarMusica': handlerCriarMusica,
    'obterMusica': handlerObterMusica,
    'listarMusicas': handlerListarMusicas,
    'atualizarMusica': handlerAtualizarMusica,
    'removerMusica': handlerRemoverMusica,
    'criarPlaylist': handlerCriarPlaylist,
    'obterPlaylist': handlerObterPlaylist,
    'listarPlaylists': handlerListarPlaylists,
    'listarPlaylistsPorUsuario': handlerListarPlaylistsPorUsuario,
    'listarMusicasPorPlaylist': handlerListarMusicasPorPlaylist,
    'listarPlaylistsPorMusica': handlerListarPlaylistsPorMusica,
    'atualizarPlaylist': handlerAtualizarPlaylist,
    'adicionarMusicaAPlaylist': handlerAdicionarMusicaAPlaylist,
    'removerMusicaDePlaylist': handlerRemoverMusicaDePlaylist,
    'removerPlaylist': handlerRemoverPlaylist,
};

const PORT = 3002;
const server = app.listen(PORT, () => {
    console.log(`🎵 Serviço SOAP rodando na porta ${PORT}`);
    console.log(`📍 WSDL: http://localhost:${PORT}/wsdl`);
    console.log(`📍 Endpoint SOAP: http://localhost:${PORT}/soap`);
});

// Remove timeout padrão do servidor - permite que requisições demorem o tempo necessário
// O objetivo é medir o tempo real de resposta, não cortar requisições lentas
server.timeout = 0; // 0 = sem timeout
