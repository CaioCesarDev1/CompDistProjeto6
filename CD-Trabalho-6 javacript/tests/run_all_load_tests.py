"""
Script para executar todos os testes de carga do Locust
Executa testes para REST, SOAP, GraphQL e gRPC com 3 configurações cada (leve, média, pesada)
"""
import subprocess
import sys
import os
import time
from datetime import datetime

# Configurações dos testes
CONFIGURACOES = {
    'leve': {'usuarios': 50, 'spawn_rate': 5},
    'media': {'usuarios': 100, 'spawn_rate': 10},
    'pesada': {'usuarios': 150, 'spawn_rate': 15}
}

# Define o diretório raiz do projeto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

APIS = {
    'rest': {
        'file': os.path.join(SCRIPT_DIR, 'locust_rest.py'),
        'host': 'http://localhost:3001',
        'name': 'REST'
    },
    'soap': {
        'file': os.path.join(SCRIPT_DIR, 'locust_soap.py'),
        'host': 'http://localhost:3002',
        'name': 'SOAP'
    },
    'graphql': {
        'file': os.path.join(SCRIPT_DIR, 'locust_graphql.py'),
        'host': 'http://localhost:3003',
        'name': 'GraphQL'
    }
}

# Diretório para salvar os resultados (na raiz do projeto)
RESULTS_DIR = os.path.join(ROOT_DIR, 'load_test_results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def executar_teste(api_key, config_key, api_config, config):
    """Executa um teste de carga específico"""
    api_name = api_config['name']
    usuarios = config['usuarios']
    spawn_rate = config['spawn_rate']
    duracao = '2m'
    
    # Prefixo para os arquivos CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_prefix = os.path.join(RESULTS_DIR, f'{api_key}_{config_key}_{timestamp}')
    
    print(f"\n{'='*70}")
    print(f"Iniciando teste: {api_name} - {config_key.upper()} ({usuarios} usuários)")
    print(f"{'='*70}")
    
    # Comando Locust (executa a partir do diretório raiz)
    cmd = [
        'locust',
        '-f', api_config['file'],
        '--headless',
        '-u', str(usuarios),
        '-r', str(spawn_rate),
        '-t', duracao,
        '--csv', csv_prefix,
        '--html', f'{csv_prefix}_report.html',
        '--loglevel', 'INFO'
    ]
    
    # Adiciona --host apenas para APIs HTTP
    if api_config['host']:
        cmd.extend(['--host', api_config['host']])
    
    try:
        print(f"Comando: {' '.join(cmd)}")
        inicio = time.time()
        
        # Executa o teste a partir do diretório raiz
        result = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=180  # 2 minutos + 1 minuto de margem
        )
        
        duracao_real = time.time() - inicio
        
        if result.returncode == 0:
            print(f"✓ Teste concluído com sucesso! (Duração: {duracao_real/60:.1f} minutos)")
            print(f"  CSVs salvos em: {csv_prefix}_*.csv")
            return True, csv_prefix
        else:
            print(f"✗ Teste falhou! (Código de saída: {result.returncode})")
            if result.stderr:
                print(f"Erro: {result.stderr[-500:]}")  # Últimos 500 caracteres
            return False, None
            
    except subprocess.TimeoutExpired:
        print(f"✗ Teste excedeu o tempo limite de 3 minutos")
        return False, None
    except Exception as e:
        print(f"✗ Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Executa todos os testes de carga"""
    print("="*70)
    print("EXECUTANDO TESTES DE CARGA - REST, SOAP e GraphQL")
    print("="*70)
    print(f"\nConfigurações por API:")
    for config_key, config in CONFIGURACOES.items():
        print(f"  - {config_key.upper()}: {config['usuarios']} usuários, spawn rate {config['spawn_rate']}/s")
    print(f"\nDuração: 2 minutos por teste")
    print(f"Total de testes: {len(APIS)} APIs × {len(CONFIGURACOES)} configurações = {len(APIS) * len(CONFIGURACOES)} testes")
    print(f"Tempo total estimado: {(len(APIS) * len(CONFIGURACOES) * 2)} minutos")
    
    resultados = {}
    
    # Executa todos os testes
    for api_key, api_config in APIS.items():
        resultados[api_key] = {}
        
        for config_key, config in CONFIGURACOES.items():
            sucesso, csv_prefix = executar_teste(api_key, config_key, api_config, config)
            resultados[api_key][config_key] = {
                'sucesso': sucesso,
                'csv_prefix': csv_prefix
            }
            
            # Aguarda um pouco entre testes
            if sucesso:
                print(f"\nAguardando 30 segundos antes do próximo teste...")
                time.sleep(30)
    
    # Resumo final
    print(f"\n{'='*70}")
    print("RESUMO DOS TESTES")
    print(f"{'='*70}")
    
    for api_key, api_config in APIS.items():
        print(f"\n{api_config['name']}:")
        for config_key in CONFIGURACOES.keys():
            resultado = resultados[api_key][config_key]
            status = "✓ SUCESSO" if resultado['sucesso'] else "✗ FALHOU"
            print(f"  {config_key.upper()}: {status}")
            if resultado['csv_prefix']:
                print(f"    CSVs: {resultado['csv_prefix']}_*.csv")
    
    print(f"\n{'='*70}")
    print(f"Todos os resultados foram salvos em: {RESULTS_DIR}/")
    print(f"{'='*70}")
    
    return resultados

if __name__ == '__main__':
    resultados = main()

