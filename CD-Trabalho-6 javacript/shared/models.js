/**
 * Modelos de dados compartilhados - versão Node.js
 */
const { v4: uuidv4 } = require('uuid');

class Usuario {
    constructor(id, nome, idade) {
        this.id = id || uuidv4();
        this.nome = nome;
        this.idade = idade;
    }
}

class Musica {
    constructor(id, nome, artista) {
        this.id = id || uuidv4();
        this.nome = nome;
        this.artista = artista;
    }
}

class Playlist {
    constructor(id, nome, usuarioId, musicasIds = []) {
        this.id = id || uuidv4();
        this.nome = nome;
        this.usuarioId = usuarioId;
        this.musicasIds = musicasIds || [];
    }
}

module.exports = {
    Usuario,
    Musica,
    Playlist
};

