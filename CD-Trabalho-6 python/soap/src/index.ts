import express from 'express';
import cors from 'cors';
import { readFileSync } from 'fs';
import { join } from 'path';
import { service } from './service';

// Usar require para biblioteca soap (compatibilidade)
const soap = require('soap');

const app = express();
const PORT = 3002;

app.use(cors());

// Servir WSDL
// Usar process.cwd() para obter o diretório de trabalho atual (soap/)
app.get('/wsdl', (req, res) => {
  const wsdl = readFileSync(join(process.cwd(), 'wsdl.wsdl'), 'utf8');
  res.set('Content-Type', 'text/xml');
  res.send(wsdl);
});

const wsdl = readFileSync(join(process.cwd(), 'wsdl.wsdl'), 'utf8');

// Criar servidor HTTP
const server = app.listen(PORT, () => {
  console.log(`Serviço SOAP rodando na porta ${PORT}`);
  console.log(`WSDL disponível em: http://localhost:${PORT}/wsdl`);
  console.log(`Endpoint SOAP: http://localhost:${PORT}/soap`);
  
  // Configurar SOAP no servidor
  soap.listen(server, '/soap', service, wsdl, () => {
    console.log('Servidor SOAP inicializado');
  });
});

