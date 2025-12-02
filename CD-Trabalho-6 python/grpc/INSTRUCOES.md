# Instruções para Gerar Arquivos gRPC

## Passo a Passo

1. **Certifique-se de que o `grpc_tools` está instalado:**
   ```bash
   pip install grpcio-tools
   ```

2. **Execute o script de geração (de qualquer diretório):**
   ```bash
   # Do diretório raiz do projeto
   python grpc/generate_proto.py
   
   # OU do diretório grpc
   cd grpc
   python generate_proto.py
   ```

3. **Verifique se os arquivos foram gerados:**
   ```bash
   ls grpc/proto/*.py
   ```
   
   Você deve ver:
   - `grpc_proto.py`
   - `grpc_proto_grpc.py`

4. **Execute o serviço gRPC:**
   ```bash
   cd grpc
   python main.py
   ```

## Solução de Problemas

### Erro: "ModuleNotFoundError: No module named 'grpc_tools'"
**Solução:** Instale o grpc_tools:
```bash
pip install grpcio-tools
```

### Erro: "No such file or directory"
**Solução:** Execute o script do diretório raiz do projeto:
```bash
python grpc/generate_proto.py
```

### Arquivos não são gerados
**Solução:** Verifique se o arquivo `grpc/proto/streaming.proto` existe e se o Python está no PATH.

## Alternativa Manual

Se o script não funcionar, você pode executar o comando diretamente:

```bash
cd grpc
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/streaming.proto
```

Depois renomeie os arquivos:
```bash
move proto\streaming_pb2.py proto\grpc_proto.py
move proto\streaming_pb2_grpc.py proto\grpc_proto_grpc.py
```


