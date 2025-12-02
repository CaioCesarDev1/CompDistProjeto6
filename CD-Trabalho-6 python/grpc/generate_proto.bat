@echo off
REM Script para gerar arquivos Python do proto no Windows

python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/streaming.proto

REM Renomear para facilitar importação
move proto\streaming_pb2.py proto\grpc_proto.py
move proto\streaming_pb2_grpc.py proto\grpc_proto_grpc.py

echo Arquivos proto gerados com sucesso!

