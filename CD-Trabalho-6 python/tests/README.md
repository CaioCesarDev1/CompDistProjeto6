# Testes de Carga

Este diretório contém os scripts de teste de carga usando k6.

## Pré-requisitos

- k6 instalado: https://k6.io/docs/getting-started/installation/

## Executando os Testes

### Teste REST
```bash
k6 run --env TEST_TYPE=rest load-tests.js
```

### Teste SOAP
```bash
k6 run --env TEST_TYPE=soap load-tests.js
```

### Teste GraphQL
```bash
k6 run --env TEST_TYPE=graphql load-tests.js
```

### Teste gRPC
```bash
# Nota: k6 não suporta gRPC nativamente
# Use ghz ou outra ferramenta especializada
ghz --proto=../grpc/proto/streaming.proto --call streaming.StreamingMusicasService.ListarMusicas -d '{}' localhost:3004
```

## Configuração dos Testes

Os testes estão configurados para:
- Ramp-up gradual de usuários
- Picos de 100 usuários simultâneos
- Thresholds de performance (95% das requisições < 500ms)
- Taxa de erro máxima de 10%

## Resultados

Os resultados dos testes serão exibidos no console e podem ser exportados em diferentes formatos:

```bash
k6 run --out json=results.json load-tests.js
k6 run --out csv=results.csv load-tests.js
```

