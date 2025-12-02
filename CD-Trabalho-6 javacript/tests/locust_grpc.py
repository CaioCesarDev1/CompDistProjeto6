"""
Teste de carga para API gRPC usando Locust
Apenas operações GET (sem modificar o banco)

Uso:
  locust -f tests/locust_grpc.py --headless -u 50 -r 5 -t 2m
  
NOTA: gRPC não usa HTTP host, então não precisa do parâmetro --host
"""
from locust import User, task, between
import sys
import os
import time

# Adiciona o diretório raiz ao path
root_dir = os.path.dirname(os.path.dirname(__file__))
proto_dir = os.path.join(root_dir, 'grpc', 'proto')
sys.path.insert(0, proto_dir)

# Importa os arquivos gerados do proto
try:
    import streaming_pb2
    import streaming_pb2_grpc
    import grpc
except ImportError as e:
    print(f"ERRO ao importar arquivos proto: {e}")
    print("Certifique-se de que os arquivos foram gerados:")
    print("  Execute: python grpc/generate_proto.py")
    streaming_pb2 = None
    streaming_pb2_grpc = None
    grpc = None


class gRPCUser(User):
    """Usuário de teste para API gRPC - apenas GETs"""
    wait_time = between(1, 3)
    
    stub = None
    channel = None
    
    def on_start(self):
        """Conecta ao servidor gRPC"""
        if grpc is None or streaming_pb2 is None or streaming_pb2_grpc is None:
            return
        
        try:
            self.channel = grpc.insecure_channel('localhost:3004')
            # Espera o canal ficar pronto
            grpc.channel_ready_future(self.channel).result(timeout=5)
            self.stub = streaming_pb2_grpc.StreamingMusicasServiceStub(self.channel)
        except Exception as e:
            self.environment.events.request_failure.fire(
                request_type="grpc",
                name="Conexão gRPC",
                response_time=0,
                exception=e,
                response_length=0
            )
    
    def on_stop(self):
        """Limpa recursos ao finalizar"""
        if self.channel:
            try:
                self.channel.close()
            except:
                pass
    
    def _call_grpc(self, method_name, request, stub_method):
        """Chama um método gRPC e reporta para o Locust"""
        if self.stub is None:
            return
        
        start_time = time.time()
        try:
            response = stub_method(request)
            response_time = int((time.time() - start_time) * 1000)
            
            # Reporta sucesso
            self.environment.events.request_success.fire(
                request_type="grpc",
                name=method_name,
                response_time=response_time,
                response_length=0
            )
            return response
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            # Reporta falha
            self.environment.events.request_failure.fire(
                request_type="grpc",
                name=method_name,
                response_time=response_time,
                exception=e,
                response_length=0
            )
    
    @task(1)
    def listar_usuarios(self):
        """Lista todos os usuários"""
        if streaming_pb2 is None or self.stub is None:
            return
        request = streaming_pb2.ListarUsuariosRequest()
        self._call_grpc("Listar Usuários (gRPC)", request, self.stub.ListarUsuarios)
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        if streaming_pb2 is None or self.stub is None:
            return
        request = streaming_pb2.ListarMusicasRequest()
        self._call_grpc("Listar Músicas (gRPC)", request, self.stub.ListarMusicas)
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        if streaming_pb2 is None or self.stub is None:
            return
        request = streaming_pb2.ListarPlaylistsRequest()
        self._call_grpc("Listar Playlists (gRPC)", request, self.stub.ListarPlaylists)

