import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');

// Configuração do teste
export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp-up: 0 a 50 usuários em 30s
    { duration: '1m', target: 50 },    // Estável: 50 usuários por 1min
    { duration: '30s', target: 0 },     // Ramp-down: 50 a 0 usuários em 30s
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% das requisições devem ser < 500ms
    errors: ['rate<0.1'],              // Taxa de erro < 10%
  },
};

const BASE_URL_REST = 'http://localhost:3001';
const BASE_URL_SOAP = 'http://localhost:3002';
const BASE_URL_GRAPHQL = 'http://localhost:3003';
const BASE_URL_GRPC = 'http://localhost:3004';

// IDs de teste (serão criados durante o teste)
let usuarioId = null;
let musicaId = null;
let playlistId = null;

// ========== TESTES REST ==========
export function testREST() {
  const baseUrl = BASE_URL_REST;
  
  // Criar usuário
  let res = http.post(`${baseUrl}/api/usuarios`, JSON.stringify({
    nome: `Usuario ${__VU}-${__ITER}`,
    idade: 25
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  const success = check(res, {
    'REST - Criar usuário status 201': (r) => r.status === 201,
  });
  errorRate.add(!success);
  
  if (res.status === 201) {
    usuarioId = JSON.parse(res.body).id;
  }
  
  sleep(0.5);
  
  // Listar usuários
  res = http.get(`${baseUrl}/api/usuarios`);
  check(res, {
    'REST - Listar usuários status 200': (r) => r.status === 200,
  });
  
  sleep(0.5);
  
  // Criar música
  res = http.post(`${baseUrl}/api/musicas`, JSON.stringify({
    nome: `Musica ${__VU}-${__ITER}`,
    artista: `Artista ${__VU}-${__ITER}`
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (res.status === 201) {
    musicaId = JSON.parse(res.body).id;
  }
  
  sleep(0.5);
  
  // Listar músicas
  res = http.get(`${baseUrl}/api/musicas`);
  check(res, {
    'REST - Listar músicas status 200': (r) => r.status === 200,
  });
  
  sleep(0.5);
  
  // Criar playlist (se tiver usuário)
  if (usuarioId) {
    res = http.post(`${baseUrl}/api/playlists`, JSON.stringify({
      nome: `Playlist ${__VU}-${__ITER}`,
      usuarioId: usuarioId
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (res.status === 201) {
      playlistId = JSON.parse(res.body).id;
    }
    
    sleep(0.5);
    
    // Listar playlists do usuário
    res = http.get(`${baseUrl}/api/usuarios/${usuarioId}/playlists`);
    check(res, {
      'REST - Listar playlists por usuário status 200': (r) => r.status === 200,
    });
    
    sleep(0.5);
    
    // Adicionar música à playlist
    if (playlistId && musicaId) {
      res = http.post(`${baseUrl}/api/playlists/${playlistId}/musicas`, JSON.stringify({
        musicaId: musicaId
      }), {
        headers: { 'Content-Type': 'application/json' },
      });
      
      sleep(0.5);
      
      // Listar músicas da playlist
      res = http.get(`${baseUrl}/api/playlists/${playlistId}/musicas`);
      check(res, {
        'REST - Listar músicas por playlist status 200': (r) => r.status === 200,
      });
    }
  }
}

// ========== TESTES SOAP ==========
export function testSOAP() {
  const baseUrl = BASE_URL_SOAP;
  
  // Criar usuário via SOAP
  const soapBody = `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <criarUsuario xmlns="http://streaming-musicas.com/soap">
      <nome>Usuario ${__VU}-${__ITER}</nome>
      <idade>25</idade>
    </criarUsuario>
  </soap:Body>
</soap:Envelope>`;
  
  let res = http.post(`${baseUrl}/soap`, soapBody, {
    headers: { 'Content-Type': 'text/xml; charset=utf-8' },
  });
  
  check(res, {
    'SOAP - Criar usuário status 200': (r) => r.status === 200,
  });
  
  sleep(0.5);
  
  // Listar usuários
  const listarSoap = `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <listarUsuarios xmlns="http://streaming-musicas.com/soap"/>
  </soap:Body>
</soap:Envelope>`;
  
  res = http.post(`${baseUrl}/soap`, listarSoap, {
    headers: { 'Content-Type': 'text/xml; charset=utf-8' },
  });
  
  check(res, {
    'SOAP - Listar usuários status 200': (r) => r.status === 200,
  });
  
  sleep(0.5);
  
  // Listar músicas
  const listarMusicasSoap = `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <listarMusicas xmlns="http://streaming-musicas.com/soap"/>
  </soap:Body>
</soap:Envelope>`;
  
  res = http.post(`${baseUrl}/soap`, listarMusicasSoap, {
    headers: { 'Content-Type': 'text/xml; charset=utf-8' },
  });
  
  check(res, {
    'SOAP - Listar músicas status 200': (r) => r.status === 200,
  });
}

// ========== TESTES GraphQL ==========
export function testGraphQL() {
  const baseUrl = BASE_URL_GRAPHQL;
  
  // Criar usuário
  const criarUsuarioQuery = {
    query: `
      mutation {
        criarUsuario(input: {
          nome: "Usuario ${__VU}-${__ITER}"
          idade: 25
        }) {
          id
          nome
          idade
        }
      }
    `
  };
  
  let res = http.post(`${baseUrl}/graphql`, JSON.stringify(criarUsuarioQuery), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(res, {
    'GraphQL - Criar usuário status 200': (r) => r.status === 200,
  });
  
  if (res.status === 200) {
    const data = JSON.parse(res.body);
    if (data.data && data.data.criarUsuario) {
      usuarioId = data.data.criarUsuario.id;
    }
  }
  
  sleep(0.5);
  
  // Listar usuários
  const listarUsuariosQuery = {
    query: `
      query {
        usuarios {
          id
          nome
          idade
        }
      }
    `
  };
  
  res = http.post(`${baseUrl}/graphql`, JSON.stringify(listarUsuariosQuery), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(res, {
    'GraphQL - Listar usuários status 200': (r) => r.status === 200,
  });
  
  sleep(0.5);
  
  // Listar músicas
  const listarMusicasQuery = {
    query: `
      query {
        musicas {
          id
          nome
          artista
        }
      }
    `
  };
  
  res = http.post(`${baseUrl}/graphql`, JSON.stringify(listarMusicasQuery), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(res, {
    'GraphQL - Listar músicas status 200': (r) => r.status === 200,
  });
  
  sleep(0.5);
  
  // Listar playlists por usuário (se tiver usuário)
  if (usuarioId) {
    const playlistsQuery = {
      query: `
        query {
          playlistsPorUsuario(usuarioId: "${usuarioId}") {
            id
            nome
            musicas {
              id
              nome
            }
          }
        }
      `
    };
    
    res = http.post(`${baseUrl}/graphql`, JSON.stringify(playlistsQuery), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    check(res, {
      'GraphQL - Listar playlists por usuário status 200': (r) => r.status === 200,
    });
  }
}

// ========== TESTES gRPC ==========
// Nota: k6 não suporta gRPC nativamente, então vamos usar HTTP/2 ou fazer requisições HTTP simples
// Para testes reais de gRPC, seria necessário usar uma ferramenta específica ou implementar um gateway HTTP
export function testGRPC() {
  // k6 não suporta gRPC diretamente
  // Em um cenário real, você usaria grpcurl ou uma ferramenta específica
  // Por enquanto, vamos apenas simular uma requisição HTTP simples
  // ou usar um gateway HTTP que converte para gRPC
  
  console.log('gRPC requer ferramentas específicas (grpcurl, bloomrpc, etc.)');
  console.log('Para testes de carga gRPC, recomenda-se usar ghz ou outra ferramenta especializada');
}

// Função principal que executa todos os testes
export default function () {
  const testType = __ENV.TEST_TYPE || 'rest';
  
  switch (testType) {
    case 'rest':
      testREST();
      break;
    case 'soap':
      testSOAP();
      break;
    case 'graphql':
      testGraphQL();
      break;
    case 'grpc':
      testGRPC();
      break;
    default:
      testREST();
  }
  
  sleep(1);
}

