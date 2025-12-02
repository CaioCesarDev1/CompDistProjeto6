"""
Script mestre: Executa todos os testes de carga e gera gráficos automaticamente
"""
import sys
import os

# Adiciona o diretório tests ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa e executa os scripts
from run_all_load_tests import main as executar_tests
from generate_graphs import main as gerar_graficos

if __name__ == '__main__':
    print("\n" + "="*70)
    print("EXECUTANDO TESTES E GERANDO GRÁFICOS")
    print("="*70)
    
    # Passo 1: Executar todos os testes
    print("\n>>> PASSO 1: Executando testes de carga...")
    resultados = executar_tests()
    
    # Passo 2: Gerar gráficos
    print("\n>>> PASSO 2: Gerando gráficos...")
    gerar_graficos()
    
    print("\n" + "="*70)
    print("PROCESSO COMPLETO!")
    print("="*70)
    print("\nTodos os resultados estão em: load_test_results/")
    print("Gráficos gerados:")
    print("  - comparacao_resultados.png (comparação geral)")
    print("  - grafico_rest.png (análise REST)")
    print("  - grafico_soap.png (análise SOAP)")
    print("  - grafico_graphql.png (análise GraphQL)")

