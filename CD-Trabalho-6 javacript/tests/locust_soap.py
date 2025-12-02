"""
Teste de carga para API SOAP usando Locust
Apenas operações GET (sem modificar o banco)

Uso:
  locust -f tests/locust_soap.py --host=http://localhost:3002 --headless -u 50 -r 5 -t 2m
"""
from locust import HttpUser, task, between


class SOAPUser(HttpUser):
    """Usuário de teste para API SOAP - apenas GETs"""
    wait_time = between(1, 3)
    host = "http://localhost:3002"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove timeout padrão - permite medir tempo real mesmo que demore muito
        self.client.timeout = None
    
    @task(1)
    def listar_usuarios(self):
        """Lista todos os usuários"""
        with self.client.get("/api/usuarios", name="Listar Usuários (SOAP)", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        with self.client.get("/api/musicas", name="Listar Músicas (SOAP)", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        with self.client.get("/api/playlists", name="Listar Playlists (SOAP)", catch_response=True) as response:
            if response.status_code == 0:
                response.failure("Conexão falhou - Status 0")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

