"""
Teste de carga para API GraphQL usando Locust
Apenas operações GET (queries, sem mutations)

Uso:
  locust -f tests/locust_graphql.py --host=http://localhost:3003 --headless -u 50 -r 5 -t 2m
"""
from locust import HttpUser, task, between
from urllib.parse import quote


class GraphQLUser(HttpUser):
    """Usuário de teste para API GraphQL - apenas queries"""
    wait_time = between(1, 3)
    host = "http://localhost:3003"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove timeout padrão - permite medir tempo real mesmo que demore muito
        self.client.timeout = None
    
    @task(1)
    def listar_usuarios(self):
        """Lista todos os usuários"""
        query = "query { usuarios { id nome idade } }"
        with self.client.get(
            f"/graphql?query={quote(query)}",
            name="Listar Usuários (GraphQL)",
            catch_response=True
            # Sem timeout - permite medir o tempo real mesmo que demore muito
        ) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                # Verifica se a resposta contém erros GraphQL
                try:
                    json_data = response.json()
                    if 'errors' in json_data and json_data['errors']:
                        response.failure(f"Erro GraphQL: {json_data['errors'][0].get('message', 'Erro desconhecido')}")
                    elif 'data' in json_data:
                        response.success()
                    else:
                        response.failure("Resposta GraphQL inválida")
                except:
                    response.failure("Erro ao parsear resposta JSON")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        query = "query { musicas { id nome artista } }"
        with self.client.get(
            f"/graphql?query={quote(query)}",
            name="Listar Músicas (GraphQL)",
            catch_response=True
            # Sem timeout - permite medir o tempo real mesmo que demore muito
        ) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                # Verifica se a resposta contém erros GraphQL
                try:
                    json_data = response.json()
                    if 'errors' in json_data and json_data['errors']:
                        response.failure(f"Erro GraphQL: {json_data['errors'][0].get('message', 'Erro desconhecido')}")
                    elif 'data' in json_data:
                        response.success()
                    else:
                        response.failure("Resposta GraphQL inválida")
                except:
                    response.failure("Erro ao parsear resposta JSON")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        query = "query { playlists { id nome usuarioId } }"
        with self.client.get(
            f"/graphql?query={quote(query)}",
            name="Listar Playlists (GraphQL)",
            catch_response=True
            # Sem timeout - permite medir o tempo real mesmo que demore muito
        ) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                # Verifica se a resposta contém erros GraphQL
                try:
                    json_data = response.json()
                    if 'errors' in json_data and json_data['errors']:
                        response.failure(f"Erro GraphQL: {json_data['errors'][0].get('message', 'Erro desconhecido')}")
                    elif 'data' in json_data:
                        response.success()
                    else:
                        response.failure("Resposta GraphQL inválida")
                except:
                    response.failure("Erro ao parsear resposta JSON")
            else:
                response.failure(f"Status code: {response.status_code}")

