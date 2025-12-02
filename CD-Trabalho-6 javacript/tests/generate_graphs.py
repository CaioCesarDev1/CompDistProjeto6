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

def calcular_estatisticas(df_stats):
    """Calcula estatísticas agregadas dos testes - usa apenas 'Listar Músicas' para comparação justa"""
    if df_stats is None or df_stats.empty:
        return None
    
    # Remove linhas completamente vazias
    df_stats = df_stats.dropna(how='all')
    
    if df_stats.empty:
        return None
    
    # Filtra apenas requisições GET
    if 'Type' in df_stats.columns:
        df_requests = df_stats[df_stats['Type'] == 'GET'].copy()
    else:
        df_requests = df_stats.copy()
    
    # Remove linhas vazias
    df_requests = df_requests.dropna(subset=['Request Count'] if 'Request Count' in df_requests.columns else [])
    
    if df_requests.empty:
        return None
    
    # FOCA APENAS EM "LISTAR MÚSICAS" para comparação justa entre APIs
    # Isso evita distorção causada por operações muito lentas como "Listar Playlists"
    musica_row = None
    if 'Name' in df_requests.columns:
        for idx, row in df_requests.iterrows():
            name = str(row['Name']).strip() if pd.notna(row['Name']) else ''
            # Procura por "Músicas" no nome (funciona para REST, SOAP e GraphQL)
            if 'Músicas' in name or 'musicas' in name.lower():
                musica_row = row
                break
    
    # Se não encontrou "Listar Músicas", usa a primeira linha GET como fallback
    if musica_row is None and not df_requests.empty:
        musica_row = df_requests.iloc[0]
    
    if musica_row is None:
        return None
    
    # Usa dados de "Listar Músicas" como representativo
    # Tratamento seguro de valores NaN e conversão
    def safe_int(val, default=0):
        try:
            if pd.isna(val):
                return default
            return int(float(val))
        except (ValueError, TypeError):
            return default
    
    def safe_float(val, default=0.0):
        try:
            if pd.isna(val):
                return default
            return float(val)
        except (ValueError, TypeError):
            return default
    
    total_requests = safe_int(musica_row.get('Request Count'), 0)
    total_failures = safe_int(musica_row.get('Failure Count'), 0)
    percentual_falha = (total_failures / total_requests * 100) if total_requests > 0 else 0
    avg_response_time = safe_float(musica_row.get('Average Response Time'), 0.0)
    median_response_time = safe_float(musica_row.get('Median Response Time'), 0.0)
    requests_per_second = safe_float(musica_row.get('Requests/s'), 0.0)
    
    return {
        'total_requests': total_requests,
        'total_failures': total_failures,
        'percentual_falha': percentual_falha,
        'avg_response_time': avg_response_time,
        'median_response_time': median_response_time,
        'requests_per_second': requests_per_second
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
                    'falha': stats['percentual_falha'],
                    'requests': stats['requests_per_second']
                })
    
    if not dados_organizados:
        print("Nenhum dado válido encontrado para gerar gráficos!")
        return
    
    # Cria gráficos comparativos (3 gráficos: tempo, falha, requests/s) - um embaixo do outro
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(18, 21))
    
    # Cores para cada configuração
    cores_config = {'LEVE': '#2ca02c', 'MEDIA': '#ff7f0e', 'PESADA': '#d62728'}
    
    # Organiza dados por API e configuração
    x_pos = 0
    x_labels = []
    x_positions = []
    tempos = []
    falhas = []
    requests = []
    cores_tempo = []
    cores_falha = []
    cores_requests = []
    
    for api_key in ['rest', 'soap', 'graphql']:
        if api_key not in dados_organizados:
            continue
        
        api_name = dados_organizados[api_key]['name']
        for config_data in dados_organizados[api_key]['configs']:
            x_labels.append(f"{api_name}\n{config_data['config']}")
            x_positions.append(x_pos)
            tempos.append(config_data['tempo'])
            falhas.append(config_data['falha'])
            requests.append(config_data['requests'])
            cores_tempo.append(cores_config.get(config_data['config'], '#1f77b4'))
            cores_falha.append(cores_config.get(config_data['config'], '#d62728'))
            cores_requests.append(cores_config.get(config_data['config'], '#9467bd'))
            x_pos += 1
        
        x_pos += 0.5  # Espaço entre APIs
    
    # Gráfico 1: Tempo de Resposta Médio
    if tempos:
        bars1 = ax1.bar(x_positions, tempos, alpha=0.8, color=cores_tempo, edgecolor='black', linewidth=0.5)
        ax1.set_xlabel('API - Configuração', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Tempo de Resposta Médio (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Tempo de Resposta Médio por API e Configuração', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_positions)
        ax1.set_xticklabels(x_labels, rotation=0, ha='center')
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
        ax2.set_xticklabels(x_labels, rotation=0, ha='center')
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adiciona valores nas barras
        max_falha = max(falhas) if falhas else 1
        for i, (pos, v) in enumerate(zip(x_positions, falhas)):
            height = max_falha * 0.02 if max_falha > 0 else 0.1
            ax2.text(pos, v + height, f'{v:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax2.legend(handles=legend_elements, loc='upper left')
    else:
        ax2.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center', transform=ax2.transAxes, fontsize=14)
    
    # Gráfico 3: Requests por Segundo
    if requests:
        bars3 = ax3.bar(x_positions, requests, alpha=0.8, color=cores_requests, edgecolor='black', linewidth=0.5)
        ax3.set_xlabel('API - Configuração', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Requests por Segundo (req/s)', fontsize=12, fontweight='bold')
        ax3.set_title('Throughput (Requests/s) por API e Configuração', fontsize=14, fontweight='bold')
        ax3.set_xticks(x_positions)
        ax3.set_xticklabels(x_labels, rotation=0, ha='center')
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adiciona valores nas barras
        max_requests = max(requests) if requests else 1
        for i, (pos, v) in enumerate(zip(x_positions, requests)):
            ax3.text(pos, v + max_requests * 0.02, f'{v:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax3.legend(handles=legend_elements, loc='upper left')
    else:
        ax3.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', va='center', transform=ax3.transAxes, fontsize=14)
    
    plt.tight_layout()
    
    # Salva gráficos
    output_file = os.path.join(RESULTS_DIR, 'comparacao_resultados.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Gráficos comparativos salvos em: {output_file}")
    print(f"  Dados plotados: {len(tempos)} barras de tempo, {len(falhas)} barras de falha, {len(requests)} barras de requests/s")
    
    # Gera gráficos separados por API
    gerar_graficos_por_api(resultados)
    
    plt.close()

def gerar_graficos_por_api(resultados):
    """Gera gráficos separados para cada API comparando as configurações"""
    for api_key, api_configs in resultados.items():
        if not any(c.get('stats') for c in api_configs.values()):
            continue
        
        api_name = api_configs.get('leve', {}).get('api_name', api_key.upper())
        configs = []
        tempos = []
        falhas = []
        requests = []
        
        for config_key in ['leve', 'media', 'pesada']:
            if config_key in api_configs and api_configs[config_key].get('stats'):
                configs.append(config_key.upper())
                tempos.append(api_configs[config_key]['stats']['avg_response_time'])
                falhas.append(api_configs[config_key]['stats']['percentual_falha'])
                requests.append(api_configs[config_key]['stats']['requests_per_second'])
        
        if not configs:
            continue
        
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(21, 5))
        
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
        
        # Gráfico de requests/s
        bars3 = ax3.bar(configs, requests, alpha=0.8, color='#9467bd', edgecolor='black', linewidth=0.5)
        ax3.set_ylabel('Requests por Segundo (req/s)', fontsize=11, fontweight='bold')
        ax3.set_title(f'{api_name} - Throughput por Configuração', fontsize=13, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        max_requests = max(requests) if requests else 1
        for i, v in enumerate(requests):
            ax3.text(i, v + max_requests * 0.02, f'{v:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
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
                print(f"  Requests por segundo: {stats['requests_per_second']:.2f} req/s")
    
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

