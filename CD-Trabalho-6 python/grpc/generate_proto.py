"""
Script Python para gerar arquivos gRPC do proto
Execute este script de qualquer diretório: python grpc/generate_proto.py
"""
import subprocess
import sys
import os

# Diretório do script (grpc/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Mudar para o diretório do script para garantir que os caminhos relativos funcionem
os.chdir(script_dir)

proto_dir = os.path.join(script_dir, 'proto')
proto_file = os.path.join(proto_dir, 'streaming.proto')

print(f"Diretório de trabalho: {os.getcwd()}")
print(f"Gerando arquivos gRPC de {proto_file}...")

try:
    # Usar caminhos relativos já que mudamos para o diretório grpc/
    result = subprocess.run([
        sys.executable, '-m', 'grpc_tools.protoc',
        '-I./proto',
        '--python_out=./proto',
        '--grpc_python_out=./proto',
        './proto/streaming.proto'
    ], check=True, capture_output=True, text=True, cwd=script_dir)
    
    # Renomear arquivos para facilitar importação
    pb2_file = os.path.join(script_dir, 'proto', 'streaming_pb2.py')
    pb2_grpc_file = os.path.join(script_dir, 'proto', 'streaming_pb2_grpc.py')
    
    if os.path.exists(pb2_file):
        grpc_proto_file = os.path.join(script_dir, 'proto', 'grpc_proto.py')
        if os.path.exists(grpc_proto_file):
            os.remove(grpc_proto_file)
        os.rename(pb2_file, grpc_proto_file)
        print(f"  ✓ Renomeado: streaming_pb2.py -> grpc_proto.py")
    else:
        print(f"  ⚠ Arquivo {pb2_file} não foi gerado!")
    
    if os.path.exists(pb2_grpc_file):
        grpc_proto_grpc_file = os.path.join(script_dir, 'proto', 'grpc_proto_grpc.py')
        if os.path.exists(grpc_proto_grpc_file):
            os.remove(grpc_proto_grpc_file)
        os.rename(pb2_grpc_file, grpc_proto_grpc_file)
        print(f"  ✓ Renomeado: streaming_pb2_grpc.py -> grpc_proto_grpc.py")
    else:
        print(f"  ⚠ Arquivo {pb2_grpc_file} não foi gerado!")
    
    print("✓ Arquivos gerados com sucesso!")
    
except subprocess.CalledProcessError as e:
    print(f"ERRO ao gerar arquivos:")
    print(e.stderr)
    sys.exit(1)
except FileNotFoundError:
    print("ERRO: grpc_tools não encontrado!")
    print("Instale com: pip install grpcio-tools")
    sys.exit(1)

