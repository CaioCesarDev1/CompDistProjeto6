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
    
    @task(1)
    def listar_usuarios(self):
        """Lista todos os usuários"""
        query = "query { usuarios { id nome idade } }"
        with self.client.get(
            f"/graphql?query={quote(query)}",
            name="Listar Usuários (GraphQL)",
            catch_response=True
        ) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        query = "query { musicas { id nome artista } }"
        with self.client.get(
            f"/graphql?query={quote(query)}",
            name="Listar Músicas (GraphQL)",
            catch_response=True
        ) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        query = "query { playlists { id nome usuarioId } }"
        with self.client.get(
            f"/graphql?query={quote(query)}",
            name="Listar Playlists (GraphQL)",
            catch_response=True
        ) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
