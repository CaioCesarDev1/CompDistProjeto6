# Serviço gRPC - Desabilitado

O serviço gRPC foi desabilitado devido à complexidade de geração dos arquivos proto.

## Alternativas

1. **Focar nas outras 3 tecnologias**: REST, SOAP e GraphQL
2. **Implementar uma API REST adicional** que simule comportamento gRPC
3. **Usar uma biblioteca alternativa** que não requer arquivos proto (se necessário no futuro)

## Para reativar o gRPC no futuro

1. Instalar `grpcio-tools`: `pip install grpcio-tools`
2. Gerar arquivos: `python grpc/generate_proto.py`
3. Executar: `python grpc/main.py`

