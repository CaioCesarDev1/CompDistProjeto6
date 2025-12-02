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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove timeout padrão - permite medir tempo real mesmo que demore muito
        self.client.timeout = None
    
    @task(1)
    def listar_usuarios(self):
        """Lista todos os usuários"""
        with self.client.get("/api/usuarios", name="Listar Usuários", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        with self.client.get("/api/musicas", name="Listar Músicas", catch_response=True, stream=False) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                # Força o download completo do conteúdo
                content = response.content
                # Verifica se recebeu dados (deve ter mais de 1MB para 15k músicas)
                if len(content) < 1000000:  # Menos de 1MB é suspeito
                    response.failure(f"Resposta muito pequena: {len(content)} bytes")
                else:
                    response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        with self.client.get("/api/playlists", name="Listar Playlists", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

