# CompDistProjeto6

Este projeto implementa e compara três tecnologias amplamente utilizadas para invocação de serviços remotos SOAP, REST e GraphQL, cada tecnologia foi implementada em duas linguagens diferentes:

- Python

- JavaScript (Node.js + Express)

Os serviços acessam um banco de dados que simula um sistema de streaming de música, contendo entidades de músicas, usuários e playlists,
as APIs foram submetidas a testes de carga e estresse utilizando Locust, analisando:

- Tempo médio de resposta

- Porcentagem de falhas

Comportamento sob diferentes quantidades de usuários simultâneos

- 50 usuários (leve)

- 100 usuários (médio)

- 150 usuários (pesado)

🏗 Arquitetura do Banco de Dados (Streaming Simulado)

![Arquitetura do Banco](./assets/arquitetura-banco.png)

3. 🧩 Tecnologias Utilizadas
Backend
Tecnologia	Python	JavaScript
REST	FastAPI / Flask	Express
SOAP	Zeep / Spyne	soap
GraphQL	Graphene / Ariadne	Apollo Server
gRPC	❌ Não implementado	❌ Não implementado
Testes de Carga

Locust (para todos os cenários)

4. 🌐 Descrição das APIs Implementadas

Cada API contém os mesmos três endpoints (ou equivalentes):

1. listarMusicas
2. listarUsuarios
3. listarPlaylists

Cada um usado com o mesmo peso nos testes do Locust.

5. 📤 Exemplos das Respostas dos Endpoints

A seguir, uma base para incluir os outputs fornecidos.

5.1 REST — Exemplo da resposta de GET /musicas

Insira aqui as primeiras 10 linhas da resposta REST:

[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nome": "Bohemian Rhapsody",
    "artista": "Queen"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",

5.2 SOAP — Exemplo da resposta de listarMusicas
{
  "musicas": [
    {
      "musica": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nome": "Bohemian Rhapsody",
        "artista": "Queen"
      }
    },
    {
      "musica": {

5.3 GraphQL — Exemplo da resposta
{
  "data": {
    "musicas": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nome": "Bohemian Rhapsody",
        "artista": "Queen"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",

6. 🧪 Estrutura dos Testes de Desempenho (Locust)

Os testes no Locust eram compostos de três chamadas com pesos iguais:

listarMusicas

listarUsuarios

listarPlaylists

E foram executados com três configurações de usuários simultâneos:

Cenário	Usuários	Descrição
Leve	50	Carga pequena
Médio	100	Carga moderada
Pesado	150	Estresse máximo
🖼 Espaço para inserir gráfico de falhas por tecnologia:
![Gráfico de Falhas](./assets/falhas.png)

🖼 Espaço para inserir gráfico de tempos médios de resposta:
![Média de Resposta](./assets/resposta-media.png)

7. 📊 Resultados Comparativos

Estrutura base para você preencher:

7.1 REST — Python vs JavaScript

Pontos para comentar (modelo):

JS apresentou menor tempo médio em cenários leves

Python apresentou maior estabilidade sob carga pesada

Falhas foram mais frequentes em listarPlaylists durante alta carga

(Preencher com seus dados reais)

7.2 SOAP — Python vs JavaScript

Sugestão de tópicos:

SOAP foi mais lento nas duas linguagens

Python manteve maior consistência

JavaScript apresentou tempo médio menor, porém com mais falhas

7.3 GraphQL — Python vs JavaScript

Sugestão de tópicos:

GraphQL em JS geralmente performa melhor devido ao ecossistema

Consultas retornam apenas campos necessários (impacto positivo)

Maior consumo de CPU nas duas linguagens em carga alta
