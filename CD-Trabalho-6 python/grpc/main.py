"""
Serviço gRPC implementado com grpcio
"""
import grpc
from concurrent import futures
import sys
import os

# Adiciona o diretório raiz ao path para imports
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)
# Adiciona o diretório proto ao path
proto_dir = os.path.join(os.path.dirname(__file__), 'proto')
sys.path.insert(0, proto_dir)

# Importa os arquivos gerados do proto
# Nota: Execute generate_proto.py primeiro para gerar estes arquivos
try:
    # Importa diretamente do diretório proto
    import importlib.util
    spec_pb2 = importlib.util.spec_from_file_location("streaming_pb2", os.path.join(proto_dir, "grpc_proto.py"))
    streaming_pb2 = importlib.util.module_from_spec(spec_pb2)
    spec_pb2.loader.exec_module(streaming_pb2)
    
    spec_grpc = importlib.util.spec_from_file_location("streaming_pb2_grpc", os.path.join(proto_dir, "grpc_proto_grpc.py"))
    streaming_pb2_grpc = importlib.util.module_from_spec(spec_grpc)
    spec_grpc.loader.exec_module(streaming_pb2_grpc)
except Exception as e:
    print(f"ERRO ao importar arquivos proto: {e}")
    print("Certifique-se de que os arquivos foram gerados:")
    print("  Execute: python grpc/generate_proto.py")
    print("  Ou: cd grpc && python generate_proto.py")
    sys.exit(1)
from sqlalchemy.orm import Session
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shared.database import get_db, init_db, SessionLocal
from shared.repository import Repositorio
from shared.models import Usuario, Musica, Playlist
import uuid


# Inicializa o banco de dados
init_db()


class StreamingMusicasService(streaming_pb2_grpc.StreamingMusicasServiceServicer):
    """Implementação do serviço gRPC"""
    
    def __init__(self):
        # Não cria sessão aqui - cada método cria sua própria sessão
        pass
    
    def _get_repo(self):
        """Cria uma nova sessão e repositório para cada requisição"""
        db = SessionLocal()
        try:
            return Repositorio(db), db
        except Exception:
            db.close()
            raise
    
    # ========== USUÁRIOS ==========
    
    def CriarUsuario(self, request, context):
        repo, db = self._get_repo()
        try:
            usuario = Usuario(
                id=str(uuid.uuid4()),
                nome=request.nome,
                idade=request.idade
            )
            criado = repo.criar_usuario(usuario)
            return streaming_pb2.UsuarioResponse(
                usuario=streaming_pb2.Usuario(
                    id=criado.id,
                    nome=criado.nome,
                    idade=criado.idade
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.UsuarioResponse(erro=str(e))
        finally:
            db.close()
    
    def ObterUsuario(self, request, context):
        repo, db = self._get_repo()
        try:
            usuario = repo.obter_usuario(request.id)
            if not usuario:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Usuário não encontrado")
                return streaming_pb2.UsuarioResponse(erro="Usuário não encontrado")
            return streaming_pb2.UsuarioResponse(
                usuario=streaming_pb2.Usuario(
                    id=usuario.id,
                    nome=usuario.nome,
                    idade=usuario.idade
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.UsuarioResponse(erro=str(e))
        finally:
            db.close()
    
    def ListarUsuarios(self, request, context):
        repo, db = self._get_repo()
        try:
            usuarios = repo.listar_usuarios()
            return streaming_pb2.ListarUsuariosResponse(
                usuarios=[
                    streaming_pb2.Usuario(
                        id=u.id,
                        nome=u.nome,
                        idade=u.idade
                    ) for u in usuarios
                ]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.ListarUsuariosResponse(erro=str(e))
        finally:
            db.close()
    
    def AtualizarUsuario(self, request, context):
        repo, db = self._get_repo()
        try:
            usuario = repo.atualizar_usuario(request.id, {
                'nome': request.nome,
                'idade': request.idade
            })
            if not usuario:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Usuário não encontrado")
                return streaming_pb2.UsuarioResponse(erro="Usuário não encontrado")
            return streaming_pb2.UsuarioResponse(
                usuario=streaming_pb2.Usuario(
                    id=usuario.id,
                    nome=usuario.nome,
                    idade=usuario.idade
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.UsuarioResponse(erro=str(e))
        finally:
            db.close()
    
    def RemoverUsuario(self, request, context):
        repo, db = self._get_repo()
        try:
            sucesso = repo.remover_usuario(request.id)
            return streaming_pb2.RemoverUsuarioResponse(sucesso=sucesso)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.RemoverUsuarioResponse(erro=str(e))
        finally:
            db.close()
    
    # ========== MÚSICAS ==========
    
    def CriarMusica(self, request, context):
        repo, db = self._get_repo()
        try:
            musica = Musica(
                id=str(uuid.uuid4()),
                nome=request.nome,
                artista=request.artista
            )
            criada = repo.criar_musica(musica)
            return streaming_pb2.MusicaResponse(
                musica=streaming_pb2.Musica(
                    id=criada.id,
                    nome=criada.nome,
                    artista=criada.artista
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.MusicaResponse(erro=str(e))
        finally:
            db.close()
    
    def ObterMusica(self, request, context):
        repo, db = self._get_repo()
        try:
            musica = repo.obter_musica(request.id)
            if not musica:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Música não encontrada")
                return streaming_pb2.MusicaResponse(erro="Música não encontrada")
            return streaming_pb2.MusicaResponse(
                musica=streaming_pb2.Musica(
                    id=musica.id,
                    nome=musica.nome,
                    artista=musica.artista
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.MusicaResponse(erro=str(e))
        finally:
            db.close()
    
    def ListarMusicas(self, request, context):
        repo, db = self._get_repo()
        try:
            musicas = repo.listar_musicas()
            return streaming_pb2.ListarMusicasResponse(
                musicas=[
                    streaming_pb2.Musica(
                        id=m.id,
                        nome=m.nome,
                        artista=m.artista
                    ) for m in musicas
                ]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.ListarMusicasResponse(erro=str(e))
        finally:
            db.close()
    
    def AtualizarMusica(self, request, context):
        repo, db = self._get_repo()
        try:
            musica = repo.atualizar_musica(request.id, {
                'nome': request.nome,
                'artista': request.artista
            })
            if not musica:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Música não encontrada")
                return streaming_pb2.MusicaResponse(erro="Música não encontrada")
            return streaming_pb2.MusicaResponse(
                musica=streaming_pb2.Musica(
                    id=musica.id,
                    nome=musica.nome,
                    artista=musica.artista
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.MusicaResponse(erro=str(e))
        finally:
            db.close()
    
    def RemoverMusica(self, request, context):
        repo, db = self._get_repo()
        try:
            sucesso = repo.remover_musica(request.id)
            return streaming_pb2.RemoverMusicaResponse(sucesso=sucesso)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.RemoverMusicaResponse(erro=str(e))
        finally:
            db.close()
    
    # ========== PLAYLISTS ==========
    
    def CriarPlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            playlist = Playlist(
                id=str(uuid.uuid4()),
                nome=request.nome,
                usuario_id=request.usuarioId,
                musicas_ids=[]
            )
            criada = repo.criar_playlist(playlist)
            return streaming_pb2.PlaylistResponse(
                playlist=streaming_pb2.Playlist(
                    id=criada.id,
                    nome=criada.nome,
                    usuarioId=criada.usuario_id,
                    musicasIds=criada.musicas_ids
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        finally:
            db.close()
    
    def ObterPlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            playlist = repo.obter_playlist(request.id)
            if not playlist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist não encontrada")
                return streaming_pb2.PlaylistResponse(erro="Playlist não encontrada")
            return streaming_pb2.PlaylistResponse(
                playlist=streaming_pb2.Playlist(
                    id=playlist.id,
                    nome=playlist.nome,
                    usuarioId=playlist.usuario_id,
                    musicasIds=playlist.musicas_ids
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        finally:
            db.close()
    
    def ListarPlaylists(self, request, context):
        repo, db = self._get_repo()
        try:
            playlists = repo.listar_playlists()
            return streaming_pb2.ListarPlaylistsResponse(
                playlists=[
                    streaming_pb2.Playlist(
                        id=p.id,
                        nome=p.nome,
                        usuarioId=p.usuario_id,
                        musicasIds=p.musicas_ids
                    ) for p in playlists
                ]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.ListarPlaylistsResponse(erro=str(e))
        finally:
            db.close()
    
    def ListarPlaylistsPorUsuario(self, request, context):
        repo, db = self._get_repo()
        try:
            playlists = repo.listar_playlists_por_usuario(request.usuarioId)
            return streaming_pb2.ListarPlaylistsResponse(
                playlists=[
                    streaming_pb2.Playlist(
                        id=p.id,
                        nome=p.nome,
                        usuarioId=p.usuario_id,
                        musicasIds=p.musicas_ids
                    ) for p in playlists
                ]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.ListarPlaylistsResponse(erro=str(e))
        finally:
            db.close()
    
    def ListarMusicasPorPlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            musicas = repo.listar_musicas_por_playlist(request.playlistId)
            return streaming_pb2.ListarMusicasResponse(
                musicas=[
                    streaming_pb2.Musica(
                        id=m.id,
                        nome=m.nome,
                        artista=m.artista
                    ) for m in musicas
                ]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.ListarMusicasResponse(erro=str(e))
        finally:
            db.close()
    
    def ListarPlaylistsPorMusica(self, request, context):
        repo, db = self._get_repo()
        try:
            playlists = repo.listar_playlists_por_musica(request.musicaId)
            return streaming_pb2.ListarPlaylistsResponse(
                playlists=[
                    streaming_pb2.Playlist(
                        id=p.id,
                        nome=p.nome,
                        usuarioId=p.usuario_id,
                        musicasIds=p.musicas_ids
                    ) for p in playlists
                ]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.ListarPlaylistsResponse(erro=str(e))
        finally:
            db.close()
    
    def AtualizarPlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            playlist = repo.atualizar_playlist(request.id, {
                'nome': request.nome,
                'usuario_id': request.usuarioId
            })
            if not playlist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist não encontrada")
                return streaming_pb2.PlaylistResponse(erro="Playlist não encontrada")
            return streaming_pb2.PlaylistResponse(
                playlist=streaming_pb2.Playlist(
                    id=playlist.id,
                    nome=playlist.nome,
                    usuarioId=playlist.usuario_id,
                    musicasIds=playlist.musicas_ids
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        finally:
            db.close()
    
    def AdicionarMusicaAPlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            playlist = repo.adicionar_musica_a_playlist(request.playlistId, request.musicaId)
            if not playlist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist não encontrada")
                return streaming_pb2.PlaylistResponse(erro="Playlist não encontrada")
            return streaming_pb2.PlaylistResponse(
                playlist=streaming_pb2.Playlist(
                    id=playlist.id,
                    nome=playlist.nome,
                    usuarioId=playlist.usuario_id,
                    musicasIds=playlist.musicas_ids
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        finally:
            db.close()
    
    def RemoverMusicaDePlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            playlist = repo.remover_musica_de_playlist(request.playlistId, request.musicaId)
            if not playlist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Playlist não encontrada")
                return streaming_pb2.PlaylistResponse(erro="Playlist não encontrada")
            return streaming_pb2.PlaylistResponse(
                playlist=streaming_pb2.Playlist(
                    id=playlist.id,
                    nome=playlist.nome,
                    usuarioId=playlist.usuario_id,
                    musicasIds=playlist.musicas_ids
                )
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        finally:
            db.close()
    
    def RemoverPlaylist(self, request, context):
        repo, db = self._get_repo()
        try:
            sucesso = repo.remover_playlist(request.id)
            return streaming_pb2.RemoverPlaylistResponse(sucesso=sucesso)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.RemoverPlaylistResponse(erro=str(e))
        finally:
            db.close()


def serve():
    PORT = 3004
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingMusicasServiceServicer_to_server(
        StreamingMusicasService(), server
    )
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()
    print(f"Serviço gRPC rodando na porta {PORT}")
    print(f"Endpoint: localhost:{PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

