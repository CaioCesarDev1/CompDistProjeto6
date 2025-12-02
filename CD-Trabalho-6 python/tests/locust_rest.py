"""
Teste de carga para API REST usando Locust
Apenas operações GET (sem modificar o banco)

Uso:
  locust -f tests/locust_rest.py --host=http://localhost:3001 --headless -u 50 -r 5 -t 2m
"""
from locust import HttpUser, task, between


class RESTUser(HttpUser):
    """Usuário de teste para API REST - apenas GETs"""
    wait_time = between(1, 3)
    host = "http://localhost:3001"
    
    @task(1)
    def listar_usuarios(self):
        """Lista todos os usuários"""
        with self.client.get("/api/usuarios", name="Listar Usuários", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        with self.client.get("/api/musicas", name="Listar Músicas", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        with self.client.get("/api/playlists", name="Listar Playlists", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
