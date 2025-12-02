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
import importlib.util

# Adiciona o diretório raiz ao path para importar módulos gRPC
root_dir = os.path.dirname(os.path.dirname(__file__))
grpc_dir = os.path.join(root_dir, 'grpc')

# IMPORTANTE: Remove completamente o diretório grpc/ do path para evitar conflito
# O diretório grpc/ do projeto conflita com o módulo grpc do pacote grpcio
sys.path = [p for p in sys.path if p != grpc_dir and not p.endswith(os.sep + 'grpc')]

# Remove o módulo grpc se ele for do diretório local
if 'grpc' in sys.modules:
    grpc_module_old = sys.modules['grpc']
    if hasattr(grpc_module_old, '__file__') and grpc_module_old.__file__:
        if root_dir in grpc_module_old.__file__ or grpc_dir in grpc_module_old.__file__:
            # É o módulo local, remove
            del sys.modules['grpc']

# Importa o módulo grpc correto (grpcio) do site-packages
# O problema é que o diretório grpc/ do projeto conflita com o módulo grpc do pacote grpcio
import importlib

# Remove o módulo grpc se existir (pode ser o diretório local)
if 'grpc' in sys.modules:
    old_grpc = sys.modules['grpc']
    if hasattr(old_grpc, '__file__') and old_grpc.__file__:
        if root_dir in old_grpc.__file__.replace('\\', '/'):
            del sys.modules['grpc']

# Remove o diretório grpc do path se estiver lá
if grpc_dir in sys.path:
    sys.path.remove(grpc_dir)

# Adiciona site-packages no início do path para garantir prioridade
import site
for site_pkg_dir in site.getsitepackages():
    if site_pkg_dir not in sys.path:
        sys.path.insert(0, site_pkg_dir)

# Agora importa o módulo grpc (deve pegar do site-packages)
try:
    grpc_module = importlib.import_module('grpc')
    # Verifica se é o módulo correto
    if not hasattr(grpc_module, '__version__'):
        # Ainda não é o correto - remove e tenta de novo sem o diretório atual
        if 'grpc' in sys.modules:
            del sys.modules['grpc']
        root_in_path = root_dir in sys.path
        if root_in_path:
            sys.path.remove(root_dir)
        grpc_module = importlib.import_module('grpc')
        if root_in_path:
            sys.path.insert(0, root_dir)
except Exception:
    # Fallback
    import grpc as grpc_module

# Garante que o módulo correto está registrado
sys.modules['grpc'] = grpc_module

# Agora adiciona o diretório raiz ao path (se ainda não estiver)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# IMPORTANTE: NUNCA adicionar o diretório grpc/ de volta ao path para evitar conflitos

# Adiciona o diretório proto ao path
proto_dir = os.path.join(root_dir, 'grpc', 'proto')
sys.path.insert(0, proto_dir)

# Importa os arquivos gerados do proto usando a mesma estratégia do grpc/main.py
grpc_proto = None
grpc_proto_grpc = None

try:
    # Carrega grpc_proto.py como módulo streaming_pb2
    spec_pb2 = importlib.util.spec_from_file_location("streaming_pb2", os.path.join(proto_dir, "grpc_proto.py"))
    streaming_pb2 = importlib.util.module_from_spec(spec_pb2)
    sys.modules["streaming_pb2"] = streaming_pb2
    spec_pb2.loader.exec_module(streaming_pb2)
    grpc_proto = streaming_pb2
    
    # O arquivo grpc_proto_grpc.py tenta importar "grpc_proto", então precisamos adicioná-lo aos módulos ANTES
    sys.modules["grpc_proto"] = streaming_pb2
    
    # Carrega grpc_proto_grpc.py como módulo streaming_pb2_grpc
    spec_grpc = importlib.util.spec_from_file_location("streaming_pb2_grpc", os.path.join(proto_dir, "grpc_proto_grpc.py"))
    streaming_pb2_grpc = importlib.util.module_from_spec(spec_grpc)
    sys.modules["streaming_pb2_grpc"] = streaming_pb2_grpc
    
    # IMPORTANTE: Remove temporariamente o diretório atual do path durante a execução do módulo
    # Isso garante que quando o módulo fizer "import grpc", ele pegue do site-packages
    root_dir_in_path_during_exec = root_dir in sys.path
    current_dir = os.getcwd()
    current_dir_in_path = current_dir in sys.path
    
    paths_to_restore = []
    if root_dir_in_path_during_exec:
        sys.path.remove(root_dir)
        paths_to_restore.append(('root_dir', root_dir))
    if current_dir_in_path and current_dir != root_dir:
        sys.path.remove(current_dir)
        paths_to_restore.append(('current_dir', current_dir))
    
    try:
        # Garante que o módulo grpc correto está em sys.modules
        sys.modules['grpc'] = grpc_module
        spec_grpc.loader.exec_module(streaming_pb2_grpc)
    finally:
        # Restaura os paths
        for name, path in reversed(paths_to_restore):
            if path not in sys.path:
                sys.path.insert(0, path)
        # Garante que o módulo correto continua em sys.modules
        sys.modules['grpc'] = grpc_module
    
    grpc_proto_grpc = streaming_pb2_grpc
    
except Exception as e:
    grpc_proto = None
    grpc_proto_grpc = None
    import traceback
    print(f"ERRO ao importar arquivos proto: {e}")
    print(traceback.format_exc())
    print("Certifique-se de que os arquivos foram gerados:")
    print("  Execute: python grpc/generate_proto.py")


class gRPCUser(User):
    """Usuário de teste para API gRPC - apenas GETs"""
    wait_time = between(1, 3)
    
    stub = None
    channel = None
    
    def on_start(self):
        """Conecta ao servidor gRPC"""
        if grpc_proto is None or grpc_proto_grpc is None:
            return
        
        try:
            # Conecta ao servidor gRPC (usa grpc_module que é o módulo correto)
            import grpc as grpc_lib
            self.channel = grpc_lib.insecure_channel('localhost:3004')
            # Espera o canal ficar pronto
            grpc_lib.channel_ready_future(self.channel).result(timeout=5)
            self.stub = grpc_proto_grpc.StreamingMusicasServiceStub(self.channel)
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
            # Importa grpc para verificar tipo de erro
            import grpc as grpc_lib
            # Reporta falha (seja RpcError ou outro tipo)
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
        if grpc_proto is None or self.stub is None:
            return
        request = grpc_proto.ListarUsuariosRequest()
        self._call_grpc("Listar Usuários (gRPC)", request, self.stub.ListarUsuarios)
    
    @task(1)
    def listar_musicas(self):
        """Lista todas as músicas"""
        if grpc_proto is None or self.stub is None:
            return
        request = grpc_proto.ListarMusicasRequest()
        self._call_grpc("Listar Músicas (gRPC)", request, self.stub.ListarMusicas)
    
    @task(1)
    def listar_playlists(self):
        """Lista todas as playlists"""
        if grpc_proto is None or self.stub is None:
            return
        request = grpc_proto.ListarPlaylistsRequest()
        self._call_grpc("Listar Playlists (gRPC)", request, self.stub.ListarPlaylists)
