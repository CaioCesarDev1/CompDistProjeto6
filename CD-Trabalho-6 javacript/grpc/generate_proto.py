"""
Script para gerar os arquivos Python a partir do arquivo .proto
Execute este script antes de rodar o servidor gRPC
"""
import subprocess
import sys
import os

# Caminho para o arquivo .proto
proto_dir = os.path.dirname(__file__)
proto_file = os.path.join(proto_dir, 'proto', 'streaming.proto')
output_dir = os.path.join(proto_dir, 'proto')

if not os.path.exists(proto_file):
    print(f"ERRO: Arquivo {proto_file} não encontrado!")
    sys.exit(1)

# Comando para gerar os arquivos Python
cmd = [
    sys.executable, '-m', 'grpc_tools.protoc',
    '--python_out=' + output_dir,
    '--grpc_python_out=' + output_dir,
    '--proto_path=' + os.path.dirname(proto_file),
    proto_file
]

print("Gerando arquivos Python a partir do .proto...")
print(f"Comando: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("✅ Arquivos gerados com sucesso!")
    print(f"   - {os.path.join(output_dir, 'streaming_pb2.py')}")
    print(f"   - {os.path.join(output_dir, 'streaming_pb2_grpc.py')}")
except subprocess.CalledProcessError as e:
    print("❌ Erro ao gerar arquivos:")
    print(e.stderr)
    sys.exit(1)

