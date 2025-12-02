#!/bin/bash

# Script para testes de carga gRPC usando ghz
# Instale ghz: go install github.com/bojand/ghz@latest

echo "Testando gRPC - Listar Músicas"
ghz --proto=../grpc/proto/streaming.proto \
    --call streaming.StreamingMusicasService.ListarMusicas \
    -d '{}' \
    -c 50 \
    -n 1000 \
    localhost:3004

echo "Testando gRPC - Criar Usuário"
ghz --proto=../grpc/proto/streaming.proto \
    --call streaming.StreamingMusicasService.CriarUsuario \
    -d '{"nome":"Usuario Teste","idade":25}' \
    -c 50 \
    -n 1000 \
    localhost:3004

