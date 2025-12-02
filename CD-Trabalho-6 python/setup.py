"""
Script de setup para o projeto
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n{'='*60}")
    print(f"Executando: {description}")
    print(f"{'='*60}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERRO ao executar: {description}")
        print(result.stderr)
        return False
    print(result.stdout)
    return True

def main():
    print("="*60)
    print("SETUP DO PROJETO - Streaming de Músicas")
    print("="*60)
    
    # 1. Verificar Python
    print("\n1. Verificando Python...")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("ERRO: Python 3.9+ é necessário!")
        sys.exit(1)
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} encontrado")
    
    # 2. Instalar dependências
    print("\n2. Instalando dependências Python...")
    if not run_command("pip install -r requirements.txt", "Instalando requirements.txt"):
        print("ERRO: Falha ao instalar dependências")
        sys.exit(1)
    
    # 3. Verificar Docker
    print("\n3. Verificando Docker...")
    result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("AVISO: Docker não encontrado. Certifique-se de ter Docker instalado para usar PostgreSQL.")
    else:
        print(f"✓ {result.stdout.strip()}")
    
    # 4. Iniciar PostgreSQL
    print("\n4. Iniciando PostgreSQL com Docker...")
    if not run_command("docker-compose up -d", "Iniciando PostgreSQL"):
        print("AVISO: Falha ao iniciar PostgreSQL. Você pode iniciar manualmente com: docker-compose up -d")
    
    # 5. Gerar arquivos gRPC
    print("\n5. Gerando arquivos gRPC...")
    os.chdir("grpc")
    if sys.platform == "win32":
        if not run_command("generate_proto.bat", "Gerando arquivos proto (Windows)"):
            print("AVISO: Falha ao gerar arquivos proto. Execute manualmente: cd grpc && generate_proto.bat")
    else:
        if not run_command("chmod +x generate_proto.sh && ./generate_proto.sh", "Gerando arquivos proto (Linux/Mac)"):
            print("AVISO: Falha ao gerar arquivos proto. Execute manualmente: cd grpc && ./generate_proto.sh")
    os.chdir("..")
    
    print("\n" + "="*60)
    print("SETUP CONCLUÍDO!")
    print("="*60)
    print("\nPróximos passos:")
    print("1. Certifique-se de que o PostgreSQL está rodando: docker-compose ps")
    print("2. Execute os serviços em terminais separados:")
    print("   - REST:    cd rest && python main.py")
    print("   - SOAP:    cd soap && python main.py")
    print("   - GraphQL: python -m graphql_py.main")
    print("   - gRPC:    cd grpc && python main.py")
    print("\n3. Para testes de carga:")
    print("   locust -f tests/locustfile.py --host=http://localhost:3001 -u 50 -r 5 -t 2m")
    print("\nConsulte README_PYTHON.md para mais informações.")

if __name__ == "__main__":
    main()

