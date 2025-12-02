"""
Serviço gRPC implementado com grpcio - versão simplificada
"""
import grpc
from concurrent import futures
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto'))

from shared.repository import get_repositorio

# Importa os arquivos gerados do proto
# Nota: Execute generate_proto.py primeiro para gerar estes arquivos
try:
    import streaming_pb2
    import streaming_pb2_grpc
except ImportError:
    print("ERRO: Arquivos proto não encontrados!")
    print("Execute primeiro: python grpc/generate_proto.py")
    sys.exit(1)

repo = get_repositorio()


class StreamingMusicasService(streaming_pb2_grpc.StreamingMusicasServiceServicer):
    """Implementação do serviço gRPC"""
    
    # ========== USUÁRIOS ==========
    
    def CriarUsuario(self, request, context):
        try:
            usuario = repo.criar_usuario(request.nome, request.idade)
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
    
    def ObterUsuario(self, request, context):
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
    
    def ListarUsuarios(self, request, context):
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
    
    def AtualizarUsuario(self, request, context):
        try:
            usuario = repo.atualizar_usuario(
                request.id,
                nome=request.nome if request.nome else None,
                idade=request.idade if request.idade else None
            )
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
    
    def RemoverUsuario(self, request, context):
        try:
            sucesso = repo.remover_usuario(request.id)
            return streaming_pb2.RemoverUsuarioResponse(sucesso=sucesso)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.RemoverUsuarioResponse(erro=str(e))
    
    # ========== MÚSICAS ==========
    
    def CriarMusica(self, request, context):
        try:
            musica = repo.criar_musica(request.nome, request.artista)
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
    
    def ObterMusica(self, request, context):
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
    
    def ListarMusicas(self, request, context):
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
    
    def AtualizarMusica(self, request, context):
        try:
            musica = repo.atualizar_musica(
                request.id,
                nome=request.nome if request.nome else None,
                artista=request.artista if request.artista else None
            )
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
    
    def RemoverMusica(self, request, context):
        try:
            sucesso = repo.remover_musica(request.id)
            return streaming_pb2.RemoverMusicaResponse(sucesso=sucesso)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.RemoverMusicaResponse(erro=str(e))
    
    # ========== PLAYLISTS ==========
    
    def CriarPlaylist(self, request, context):
        try:
            playlist = repo.criar_playlist(request.nome, request.usuarioId)
            return streaming_pb2.PlaylistResponse(
                playlist=streaming_pb2.Playlist(
                    id=playlist.id,
                    nome=playlist.nome,
                    usuarioId=playlist.usuario_id,
                    musicasIds=playlist.musicas_ids
                )
            )
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
    
    def ObterPlaylist(self, request, context):
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
    
    def ListarPlaylists(self, request, context):
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
    
    def ListarPlaylistsPorUsuario(self, request, context):
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
    
    def ListarMusicasPorPlaylist(self, request, context):
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
    
    def ListarPlaylistsPorMusica(self, request, context):
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
    
    def AtualizarPlaylist(self, request, context):
        try:
            playlist = repo.atualizar_playlist(
                request.id,
                nome=request.nome if request.nome else None,
                usuario_id=request.usuarioId if request.usuarioId else None
            )
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
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
    
    def AdicionarMusicaAPlaylist(self, request, context):
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
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistResponse(erro=str(e))
    
    def RemoverMusicaDePlaylist(self, request, context):
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
    
    def RemoverPlaylist(self, request, context):
        try:
            sucesso = repo.remover_playlist(request.id)
            return streaming_pb2.RemoverPlaylistResponse(sucesso=sucesso)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.RemoverPlaylistResponse(erro=str(e))


def serve():
    """Inicia o servidor gRPC"""
    PORT = 3004
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingMusicasServiceServicer_to_server(
        StreamingMusicasService(), server
    )
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()
    print(f"🎵 Serviço gRPC rodando na porta {PORT}")
    print(f"📍 Endpoint: localhost:{PORT}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

