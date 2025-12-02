#!/bin/bash
# Script para gerar arquivos Python do proto

python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/streaming.proto

# Renomear para facilitar importação
mv proto/streaming_pb2.py proto/grpc_proto.py
mv proto/streaming_pb2_grpc.py proto/grpc_proto_grpc.py

echo "Arquivos proto gerados com sucesso!"

