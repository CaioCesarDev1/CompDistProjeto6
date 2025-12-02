# Testes de Carga Automatizados

Scripts para executar testes de carga completos e gerar gráficos comparativos.

## Scripts Disponíveis

### 1. `run_all_load_tests.py`
Executa todos os testes de carga para REST, SOAP e GraphQL.

**Configurações:**
- **Leve**: 50 usuários, spawn rate 5/s, 10 minutos
- **Média**: 100 usuários, spawn rate 10/s, 10 minutos  
- **Pesada**: 150 usuários, spawn rate 15/s, 10 minutos

**Total**: 9 testes (3 APIs × 3 configurações)

### 2. `generate_graphs.py`
Processa os CSVs gerados e cria gráficos comparativos.

### 3. `run_tests_and_generate_graphs.py` ⭐
Script mestre que executa tudo automaticamente (testes + gráficos).

## Uso

### Opção 1: Executar tudo de uma vez (Recomendado)
```bash
python tests/run_tests_and_generate_graphs.py
```

### Opção 2: Executar separadamente
```bash
# 1. Executar testes
python tests/run_all_load_tests.py

# 2. Gerar gráficos
python tests/generate_graphs.py
```

## Pré-requisitos

1. Servidores rodando:
   - REST: `http://localhost:3001`
   - SOAP: `http://localhost:3002`
   - GraphQL: `http://localhost:3003`

2. Dependências instaladas:
```bash
pip install locust pandas matplotlib
```

## Resultados

Todos os resultados são salvos em `load_test_results/`:

### Arquivos CSV
- `{api}_{config}_{timestamp}_stats.csv` - Estatísticas gerais
- `{api}_{config}_{timestamp}_failures.csv` - Falhas detalhadas
- `{api}_{config}_{timestamp}_exceptions.csv` - Exceções
- `{api}_{config}_{timestamp}_report.html` - Relatório HTML

### Gráficos Gerados
- `comparacao_resultados.png` - Comparação geral de todas as APIs
- `grafico_rest.png` - Análise detalhada REST
- `grafico_soap.png` - Análise detalhada SOAP
- `grafico_graphql.png` - Análise detalhada GraphQL

Cada gráfico mostra:
- **Tempo de resposta médio** (ms)
- **Percentual de falha** (%)

## Tempo Total Estimado

- Cada teste: 10 minutos
- Total de testes: 9
- Intervalo entre testes: 30 segundos
- **Tempo total**: ~95 minutos (~1h35min)

## Exemplo de Saída

```
REST - LEVE:
  Total de requisições: 15,234
  Total de falhas: 45
  Percentual de falha: 0.30%
  Tempo de resposta médio: 125.5ms
```

