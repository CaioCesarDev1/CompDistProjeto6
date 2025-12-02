/**
 * Configuração do banco de dados PostgreSQL
 */
const { Pool } = require('pg');
require('dotenv').config();

// Configuração do banco de dados usando variáveis de ambiente
const DB_USER = process.env.DB_USER || 'streaming_user';
const DB_PASSWORD = process.env.DB_PASSWORD || 'streaming_pass';
const DB_HOST = process.env.DB_HOST || 'localhost';
const DB_PORT = parseInt(process.env.DB_PORT || '5433');
const DB_NAME = process.env.DB_NAME || 'streaming_db';

// Pool de conexões para melhor performance
const pool = new Pool({
    user: DB_USER,
    password: DB_PASSWORD,
    host: DB_HOST,
    port: DB_PORT,
    database: DB_NAME,
    max: 20, // Máximo de conexões no pool
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 10000, // Timeout apenas para estabelecer conexão (não para queries)
    // SEM statement_timeout - permite que queries demorem o tempo necessário para completar
    // O objetivo é medir o tempo real de resposta, não cortar requisições lentas
});

// Testa a conexão ao inicializar
pool.on('connect', () => {
    console.log('✅ Conectado ao PostgreSQL');
});

pool.on('error', (err) => {
    console.error('❌ Erro inesperado no pool de conexões:', err);
});

/**
 * Executa uma query e retorna os resultados
 */
async function query(text, params) {
    const start = Date.now();
    try {
        const res = await pool.query(text, params);
        const duration = Date.now() - start;
        // console.log('Query executada', { text, duration, rows: res.rowCount });
        return res;
    } catch (error) {
        console.error('Erro na query:', { 
            text: text.substring(0, 100), // Primeiros 100 caracteres
            params: params ? params.length : 0,
            error: error.message,
            code: error.code
        });
        // Re-throw com mensagem mais clara
        const errorMessage = error.code === 'ECONNREFUSED' 
            ? 'Não foi possível conectar ao banco de dados PostgreSQL. Verifique se o banco está rodando na porta 5433.'
            : error.message;
        throw new Error(errorMessage);
    }
}

/**
 * Obtém um cliente do pool para transações
 */
async function getClient() {
    return await pool.connect();
}

/**
 * Fecha todas as conexões do pool
 */
async function close() {
    await pool.end();
}

module.exports = {
    pool,
    query,
    getClient,
    close
};

