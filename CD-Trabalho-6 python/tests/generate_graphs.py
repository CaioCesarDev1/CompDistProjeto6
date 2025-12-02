"""
Script para processar CSVs do Locust e gerar gráficos
Gera gráficos de tempo de resposta e % de falha
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usa backend não-interativo
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
import glob
from pathlib import Path

# Define o diretório de resultados (na raiz do projeto)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
RESULTS_DIR = os.path.join(ROOT_DIR, 'load_test_results')

def processar_csv_stats(csv_file):
    """Processa o arquivo CSV de estatísticas do Locust"""
    try:
        # Tenta diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file, encoding=encoding, skip_blank_lines=True)
                break
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        
        if df is None:
            print(f"Erro: Não foi possível ler {csv_file} com nenhum encoding")
            return None
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        return df
    except Exception as e:
        print(f"Erro ao processar {csv_file}: {e}")
        import traceback
        traceback.print_exc()
        return None

def processar_csv_requests(csv_file):
    """Processa o arquivo CSV de requisições do Locust"""
    try:
        df = pd.read_csv(csv_file)
        # Colunas esperadas: Timestamp, Type, Name, Response Time, Response Length, Exception
        return df
    except Exception as e:
        print(f"Erro ao processar {csv_file}: {e}")
        return None

def calcular_estatisticas(df_stats):
    """Calcula estatísticas agregadas dos testes"""
    if df_stats is None or df_stats.empty:
        return None
    
    # Remove linhas completamente vazias
    df_stats = df_stats.dropna(how='all')
    
    if df_stats.empty:
        return None
    
    # Tenta usar a linha "Aggregated" que tem os totais (mais confiável)
    aggregated = None
    
    # Procura linha Aggregated - Type está vazio e Name é "Aggregated"
    if 'Type' in df_stats.columns and 'Name' in df_stats.columns:
        for idx, row in df_stats.iterrows():
            type_val = str(row['Type']).strip() if pd.notna(row['Type']) else ''
            name_val = str(row['Name']).strip() if pd.notna(row['Name']) else ''
            
            # Linha Aggregated tem Type vazio e Name = "Aggregated"
            if (type_val == '' or type_val == 'nan') and name_val == 'Aggregated':
                aggregated = row
                break
    
    # Se não encontrou Aggregated, calcula a partir das linhas GET
    if aggregated is None:
        # Filtra apenas requisições GET
        if 'Type' in df_stats.columns:
            df_requests = df_stats[df_stats['Type'] == 'GET'].copy()
        else:
            df_requests = df_stats.copy()
        
        # Remove linhas vazias
        df_requests = df_requests.dropna(subset=['Request Count'] if 'Request Count' in df_requests.columns else [])
        
        if df_requests.empty:
            return None
        
        # Calcula totais
        total_requests = int(df_requests['Request Count'].sum())
        total_failures = int(df_requests['Failure Count'].sum())
        percentual_falha = (total_failures / total_requests * 100) if total_requests > 0 else 0
        
        # Tempo de resposta médio (weighted by request count)
        if 'Average Response Time' in df_requests.columns and 'Request Count' in df_requests.columns:
            avg_response_time = (df_requests['Average Response Time'] * df_requests['Request Count']).sum() / total_requests if total_requests > 0 else 0
        else:
            avg_response_time = 0
        
        # Tempo de resposta mediano (média dos medianos ponderada)
        if 'Median Response Time' in df_requests.columns:
            median_response_time = (df_requests['Median Response Time'] * df_requests['Request Count']).sum() / total_requests if total_requests > 0 else df_requests['Median Response Time'].max()
        else:
            median_response_time = 0
    else:
        # Usa dados da linha Aggregated
        total_requests = int(aggregated['Request Count']) if pd.notna(aggregated.get('Request Count')) else 0
        total_failures = int(aggregated['Failure Count']) if pd.notna(aggregated.get('Failure Count')) else 0
        percentual_falha = (total_failures / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = float(aggregated['Average Response Time']) if pd.notna(aggregated.get('Average Response Time')) else 0
        median_response_time = float(aggregated['Median Response Time']) if pd.notna(aggregated.get('Median Response Time')) else 0
    
    return {
        'total_requests': total_requests,
        'total_failures': total_failures,
        'percentual_falha': percentual_falha,
        'avg_response_time': avg_response_time,
        'median_response_time': median_response_time
    }

def gerar_graficos(resultados):
    """Gera gráficos comparativos dos resultados"""
    # Organiza dados para gráficos - agrupa por API primeiro
    dados_organizados = {}
    
    for api_key, api_configs in resultados.items():
        if api_key not in dados_organizados:
            api_names = {
                'rest': 'REST',
                'soap': 'SOAP',
                'graphql': 'GraphQL'
            }
            dados_organizados[api_key] = {
                'name': api_names.get(api_key, api_key.upper()),
                'configs': []
            }
        
        for config_key in ['leve', 'media', 'pesada']:
            if config_key in api_configs and api_configs[config_key]['stats']:
                stats = api_configs[config_key]['stats']
                dados_organizados[api_key]['configs'].append({
                    'config': config_key.upper(),
                    'tempo': stats['avg_response_time'],
                    'falha': stats['percentual_falha']
                })
    
    if not dados_organizados:
        print("Nenhum dado válido encontrado para gerar gráficos!")
        return
    
    # Cria gráficos comparativos
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    # Cores para cada configuração
    cores_config = {'LEVE': '#2ca02c', 'MEDIA': '#ff7f0e', 'PESADA': '#d62728'}
    
    # Organiza dados por API e configuração
    x_pos = 0
    x_labels = []
    x_positions = []
    tempos = []
    falhas = []
    cores_tempo = []
    cores_falha = []
    
    for api_key in ['rest', 'soap', 'graphql']:
        if api_key not in dados_organizados:
            continue
        
        api_name = dados_organizados[api_key]['name']
        for config_data in dados_organizados[api_key]['configs']:
            x_labels.append(f"{api_name}\n{config_data['config']}")
            x_positions.append(x_pos)
            tempos.append(config_data['tempo'])
            falhas.append(config_data['falha'])
            cores_tempo.append(cores_config.get(config_data['config'], '#1f77b4'))
            cores_falha.append(cores_config.get(config_data['config'], '#d62728'))
            x_pos += 1
        
        x_pos += 0.5  # Espaço entre APIs
    
    # Gráfico 1: Tempo de Resposta Médio
    if tempos:
        bars1 = ax1.bar(x_positions, tempos, alpha=0.8, color=cores_tempo, edgecolor='black', linewidth=0.5)
        ax1.set_xlabel('API - Configuração', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Tempo de Resposta Médio (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Tempo de Resposta Médio por API e Configuração', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_positions)
        ax1.set_xticklabels(x_labels, rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adiciona valores nas barras
        max_tempo = max(tempos) if tempos else 1
        for i, (pos, v) in enumerate(zip(x_positions, tempos)):
            ax1.text(pos, v + max_tempo * 0.02, f'{v:.0f}ms', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Formata eixo Y para melhor visualização
        ax1.ticklabel_format(style='plain', axis='y')
    else:
        ax1.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center', transform=ax1.transAxes, fontsize=14)
    
    # Adiciona legenda
    legend_elements = [Patch(facecolor=cores_config['LEVE'], label='Leve (50 users)'),
                      Patch(facecolor=cores_config['MEDIA'], label='Média (100 users)'),
                      Patch(facecolor=cores_config['PESADA'], label='Pesada (150 users)')]
    ax1.legend(handles=legend_elements, loc='upper left')
    
    # Gráfico 2: Percentual de Falha
    if falhas:
        bars2 = ax2.bar(x_positions, falhas, alpha=0.8, color=cores_falha, edgecolor='black', linewidth=0.5)
        ax2.set_xlabel('API - Configuração', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentual de Falha (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Percentual de Falha por API e Configuração', fontsize=14, fontweight='bold')
        ax2.set_xticks(x_positions)
        ax2.set_xticklabels(x_labels, rotation=45, ha='right')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adiciona valores nas barras
        max_falha = max(falhas) if falhas else 1
        for i, (pos, v) in enumerate(zip(x_positions, falhas)):
            height = max_falha * 0.02 if max_falha > 0 else 0.1
            ax2.text(pos, v + height, f'{v:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax2.legend(handles=legend_elements, loc='upper left')
    else:
        ax2.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center', transform=ax2.transAxes, fontsize=14)
    
    plt.tight_layout()
    
    # Salva gráficos
    output_file = os.path.join(RESULTS_DIR, 'comparacao_resultados.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Gráficos comparativos salvos em: {output_file}")
    print(f"  Dados plotados: {len(tempos)} barras de tempo, {len(falhas)} barras de falha")
    
    # Gera gráficos separados por API
    gerar_graficos_por_api(resultados)
    
    plt.close()

def gerar_graficos_por_api(resultados):
    """Gera gráficos separados para cada API comparando as configurações"""
    for api_key, api_configs in resultados.items():
        if not any(c['stats'] for c in api_configs.values()):
            continue
        
        api_name = list(api_configs.values())[0]['api_name']
        configs = []
        tempos = []
        falhas = []
        
        for config_key in ['leve', 'media', 'pesada']:
            if config_key in api_configs and api_configs[config_key]['stats']:
                configs.append(config_key.upper())
                tempos.append(api_configs[config_key]['stats']['avg_response_time'])
                falhas.append(api_configs[config_key]['stats']['percentual_falha'])
        
        if not configs:
            continue
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Gráfico de tempo de resposta
        bars1 = ax1.bar(configs, tempos, alpha=0.8, color='#1f77b4', edgecolor='black', linewidth=0.5)
        ax1.set_ylabel('Tempo de Resposta Médio (ms)', fontsize=11, fontweight='bold')
        ax1.set_title(f'{api_name} - Tempo de Resposta por Configuração', fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        max_tempo = max(tempos) if tempos else 1
        for i, v in enumerate(tempos):
            ax1.text(i, v + max_tempo * 0.02, f'{v:.0f}ms', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax1.ticklabel_format(style='plain', axis='y')
        
        # Gráfico de % de falha
        bars2 = ax2.bar(configs, falhas, alpha=0.8, color='#d62728', edgecolor='black', linewidth=0.5)
        ax2.set_ylabel('Percentual de Falha (%)', fontsize=11, fontweight='bold')
        ax2.set_title(f'{api_name} - Percentual de Falha por Configuração', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        max_falha = max(falhas) if falhas else 1
        for i, v in enumerate(falhas):
            height = max_falha * 0.02 if max_falha > 0 else 0.1
            ax2.text(i, v + height, f'{v:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        output_file = os.path.join(RESULTS_DIR, f'grafico_{api_key}.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Gráfico de {api_name} salvo em: {output_file}")
        print(f"  Configurações: {', '.join(configs)}")
        plt.close()

def main():
    """Processa CSVs e gera gráficos"""
    print("="*70)
    print("PROCESSANDO RESULTADOS DOS TESTES DE CARGA")
    print("="*70)
    
    if not os.path.exists(RESULTS_DIR):
        print(f"Erro: Diretório {RESULTS_DIR} não encontrado!")
        print("Execute primeiro: python tests/run_all_load_tests.py")
        return
    
    # Procura todos os arquivos CSV de estatísticas
    csv_files = glob.glob(os.path.join(RESULTS_DIR, '*_stats.csv'))
    
    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em {RESULTS_DIR}/")
        return
    
    print(f"\nEncontrados {len(csv_files)} arquivos CSV")
    
    # Organiza resultados por API e configuração
    resultados = {}
    
    for csv_file in csv_files:
        # Extrai API e configuração do nome do arquivo
        filename = os.path.basename(csv_file)
        # Formato esperado: {api}_{config}_{timestamp}_stats.csv
        parts = filename.replace('_stats.csv', '').split('_')
        if len(parts) >= 2:
            api_key = parts[0]
            config_key = parts[1]
            
            if api_key not in resultados:
                resultados[api_key] = {}
            
            # Nome da API
            api_names = {
                'rest': 'REST',
                'soap': 'SOAP',
                'graphql': 'GraphQL'
            }
            
            # Processa o CSV
            df_stats = processar_csv_stats(csv_file)
            stats = calcular_estatisticas(df_stats)
            
            resultados[api_key][config_key] = {
                'api_name': api_names.get(api_key, api_key.upper()),
                'csv_file': csv_file,
                'stats': stats
            }
            
            if stats:
                print(f"\n{api_names.get(api_key, api_key)} - {config_key.upper()}:")
                print(f"  Total de requisições: {stats['total_requests']:,}")
                print(f"  Total de falhas: {stats['total_failures']:,}")
                print(f"  Percentual de falha: {stats['percentual_falha']:.2f}%")
                print(f"  Tempo de resposta médio: {stats['avg_response_time']:.1f}ms")
                print(f"  Tempo de resposta mediano: {stats['median_response_time']:.1f}ms")
    
    # Gera gráficos
    print(f"\n{'='*70}")
    print("GERANDO GRÁFICOS")
    print(f"{'='*70}")
    gerar_graficos(resultados)
    
    print(f"\n{'='*70}")
    print("PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()

