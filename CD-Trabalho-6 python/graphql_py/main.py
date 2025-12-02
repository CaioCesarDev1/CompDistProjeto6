"""
Serviço GraphQL implementado com Graphene e FastAPI.
Executar com: python -m graphql_py.main
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import uuid
import sys
import os
from contextlib import contextmanager

# Configura o diretório raiz do projeto
root_dir = os.path.dirname(os.path.dirname(__file__))

import graphene  # type: ignore

# Reinsere o diretório raiz para importar módulos locais
sys.path.insert(0, root_dir)

from shared.database import get_db, init_db
from shared.repository import Repositorio
from shared.models import Usuario, Musica, Playlist

# Inicializa o banco de dados
init_db()


@contextmanager
def repo_context():
    """Retorna o repositório garantindo o fechamento da sessão."""
    db_gen = get_db()
    db = next(db_gen)
    try:
        yield Repositorio(db)
    finally:
        try:
            db_gen.close()
        except Exception:
            pass


def to_usuario(usuario: Usuario):
    if not usuario:
        return None
    return UsuarioType(id=usuario.id, nome=usuario.nome, idade=usuario.idade)


def to_musica(musica: Musica):
    if not musica:
        return None
    return MusicaType(id=musica.id, nome=musica.nome, artista=musica.artista)


def to_playlist(playlist: Playlist):
    if not playlist:
        return None
    return PlaylistType(
        id=playlist.id,
        nome=playlist.nome,
        usuario_id=playlist.usuario_id,
        musicas_ids=playlist.musicas_ids or []
    )


class UsuarioType(graphene.ObjectType):
    id = graphene.String()
    nome = graphene.String()
    idade = graphene.Int()
    playlists = graphene.List(lambda: PlaylistType)

    def resolve_playlists(parent, info):
        with repo_context() as repo:
            playlists = repo.listar_playlists_por_usuario(parent.id)
            return [to_playlist(p) for p in playlists]


class MusicaType(graphene.ObjectType):
    id = graphene.String()
    nome = graphene.String()
    artista = graphene.String()
    playlists = graphene.List(lambda: PlaylistType)

    def resolve_playlists(parent, info):
        with repo_context() as repo:
            playlists = repo.listar_playlists_por_musica(parent.id)
            return [to_playlist(p) for p in playlists]


class PlaylistType(graphene.ObjectType):
    id = graphene.String()
    nome = graphene.String()
    usuario_id = graphene.String()
    musicas_ids = graphene.List(graphene.String)
    usuario = graphene.Field(UsuarioType)
    musicas = graphene.List(MusicaType)

    def resolve_usuario(parent, info):
        with repo_context() as repo:
            usuario = repo.obter_usuario(parent.usuario_id)
            return to_usuario(usuario)

    def resolve_musicas(parent, info):
        with repo_context() as repo:
            musicas = repo.listar_musicas_por_playlist(parent.id)
            return [to_musica(m) for m in musicas]


class UsuarioInput(graphene.InputObjectType):
    nome = graphene.String(required=True)
    idade = graphene.Int(required=True)


class UsuarioUpdateInput(graphene.InputObjectType):
    nome = graphene.String()
    idade = graphene.Int()


class MusicaInput(graphene.InputObjectType):
    nome = graphene.String(required=True)
    artista = graphene.String(required=True)


class MusicaUpdateInput(graphene.InputObjectType):
    nome = graphene.String()
    artista = graphene.String()


class PlaylistInput(graphene.InputObjectType):
    nome = graphene.String(required=True)
    usuario_id = graphene.String(required=True)


class PlaylistUpdateInput(graphene.InputObjectType):
    nome = graphene.String()
    usuario_id = graphene.String()


class Query(graphene.ObjectType):
    usuario = graphene.Field(UsuarioType, id=graphene.String(required=True))
    usuarios = graphene.List(UsuarioType)
    musica = graphene.Field(MusicaType, id=graphene.String(required=True))
    musicas = graphene.List(MusicaType)
    playlist = graphene.Field(PlaylistType, id=graphene.String(required=True))
    playlists = graphene.List(PlaylistType)
    playlists_por_usuario = graphene.List(PlaylistType, usuario_id=graphene.String(required=True))
    musicas_por_playlist = graphene.List(MusicaType, playlist_id=graphene.String(required=True))
    playlists_por_musica = graphene.List(PlaylistType, musica_id=graphene.String(required=True))

    def resolve_usuario(root, info, id):
        with repo_context() as repo:
            return to_usuario(repo.obter_usuario(id))

    def resolve_usuarios(root, info):
        with repo_context() as repo:
            return [to_usuario(u) for u in repo.listar_usuarios()]

    def resolve_musica(root, info, id):
        with repo_context() as repo:
            return to_musica(repo.obter_musica(id))

    def resolve_musicas(root, info):
        with repo_context() as repo:
            return [to_musica(m) for m in repo.listar_musicas()]

    def resolve_playlist(root, info, id):
        with repo_context() as repo:
            return to_playlist(repo.obter_playlist(id))

    def resolve_playlists(root, info):
        with repo_context() as repo:
            return [to_playlist(p) for p in repo.listar_playlists()]

    def resolve_playlists_por_usuario(root, info, usuario_id):
        with repo_context() as repo:
            return [to_playlist(p) for p in repo.listar_playlists_por_usuario(usuario_id)]

    def resolve_musicas_por_playlist(root, info, playlist_id):
        with repo_context() as repo:
            return [to_musica(m) for m in repo.listar_musicas_por_playlist(playlist_id)]

    def resolve_playlists_por_musica(root, info, musica_id):
        with repo_context() as repo:
            return [to_playlist(p) for p in repo.listar_playlists_por_musica(musica_id)]


class CriarUsuario(graphene.Mutation):
    class Arguments:
        input = UsuarioInput(required=True)

    usuario = graphene.Field(UsuarioType)

    def mutate(root, info, input):
        with repo_context() as repo:
            usuario = Usuario(id=str(uuid.uuid4()), nome=input.nome, idade=input.idade)
            criado = repo.criar_usuario(usuario)
            return CriarUsuario(usuario=to_usuario(criado))


class AtualizarUsuario(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = UsuarioUpdateInput(required=True)

    usuario = graphene.Field(UsuarioType)

    def mutate(root, info, id, input):
        dados = {k: v for k, v in input.items() if v is not None}
        with repo_context() as repo:
            atualizado = repo.atualizar_usuario(id, dados)
            return AtualizarUsuario(usuario=to_usuario(atualizado))


class RemoverUsuario(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    mensagem = graphene.String()

    def mutate(root, info, id):
        with repo_context() as repo:
            if repo.remover_usuario(id):
                return RemoverUsuario(mensagem="Usuário removido com sucesso")
            return RemoverUsuario(mensagem="Usuário não encontrado")


class CriarMusica(graphene.Mutation):
    class Arguments:
        input = MusicaInput(required=True)

    musica = graphene.Field(MusicaType)

    def mutate(root, info, input):
        with repo_context() as repo:
            musica = Musica(id=str(uuid.uuid4()), nome=input.nome, artista=input.artista)
            criada = repo.criar_musica(musica)
            return CriarMusica(musica=to_musica(criada))


class AtualizarMusica(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = MusicaUpdateInput(required=True)

    musica = graphene.Field(MusicaType)

    def mutate(root, info, id, input):
        dados = {k: v for k, v in input.items() if v is not None}
        with repo_context() as repo:
            atualizada = repo.atualizar_musica(id, dados)
            return AtualizarMusica(musica=to_musica(atualizada))


class RemoverMusica(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    mensagem = graphene.String()

    def mutate(root, info, id):
        with repo_context() as repo:
            if repo.remover_musica(id):
                return RemoverMusica(mensagem="Música removida com sucesso")
            return RemoverMusica(mensagem="Música não encontrada")


class CriarPlaylist(graphene.Mutation):
    class Arguments:
        input = PlaylistInput(required=True)

    playlist = graphene.Field(PlaylistType)

    def mutate(root, info, input):
        with repo_context() as repo:
            playlist = Playlist(
                id=str(uuid.uuid4()),
                nome=input.nome,
                usuario_id=input.usuario_id,
                musicas_ids=[]
            )
            criada = repo.criar_playlist(playlist)
            return CriarPlaylist(playlist=to_playlist(criada))


class AtualizarPlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        input = PlaylistUpdateInput(required=True)

    playlist = graphene.Field(PlaylistType)

    def mutate(root, info, id, input):
        dados = {}
        if input.nome is not None:
            dados["nome"] = input.nome
        if input.usuario_id is not None:
            dados["usuario_id"] = input.usuario_id
        with repo_context() as repo:
            atualizada = repo.atualizar_playlist(id, dados)
            return AtualizarPlaylist(playlist=to_playlist(atualizada))


class AdicionarMusicaAPlaylist(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.String(required=True)
        musica_id = graphene.String(required=True)

    playlist = graphene.Field(PlaylistType)

    def mutate(root, info, playlist_id, musica_id):
        with repo_context() as repo:
            try:
                playlist = repo.adicionar_musica_a_playlist(playlist_id, musica_id)
                return AdicionarMusicaAPlaylist(playlist=to_playlist(playlist))
            except ValueError as exc:
                raise Exception(str(exc))


class RemoverMusicaDePlaylist(graphene.Mutation):
    class Arguments:
        playlist_id = graphene.String(required=True)
        musica_id = graphene.String(required=True)

    playlist = graphene.Field(PlaylistType)

    def mutate(root, info, playlist_id, musica_id):
        with repo_context() as repo:
            playlist = repo.remover_musica_de_playlist(playlist_id, musica_id)
            return RemoverMusicaDePlaylist(playlist=to_playlist(playlist))


class RemoverPlaylist(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    mensagem = graphene.String()

    def mutate(root, info, id):
        with repo_context() as repo:
            if repo.remover_playlist(id):
                return RemoverPlaylist(mensagem="Playlist removida com sucesso")
            return RemoverPlaylist(mensagem="Playlist não encontrada")


class Mutation(graphene.ObjectType):
    criar_usuario = CriarUsuario.Field()
    atualizar_usuario = AtualizarUsuario.Field()
    remover_usuario = RemoverUsuario.Field()
    criar_musica = CriarMusica.Field()
    atualizar_musica = AtualizarMusica.Field()
    remover_musica = RemoverMusica.Field()
    criar_playlist = CriarPlaylist.Field()
    atualizar_playlist = AtualizarPlaylist.Field()
    adicionar_musica_a_playlist = AdicionarMusicaAPlaylist.Field()
    remover_musica_de_playlist = RemoverMusicaDePlaylist.Field()
    remover_playlist = RemoverPlaylist.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

app = FastAPI(title="Streaming de Músicas - GraphQL API", version="1.0.0")


@app.post("/graphql")
async def graphql_endpoint(request: Request):
    """Endpoint GraphQL"""
    try:
        body = await request.json()
        query = body.get("query")
        variables = body.get("variables")
        operation_name = body.get("operationName")

        if not query:
            return JSONResponse({"errors": [{"message": "Query não fornecida"}]}, status_code=400)

        result = schema.execute(
            query,
            variable_values=variables,
            operation_name=operation_name
        )

        if result.errors:
            return JSONResponse({"errors": [{"message": str(e)} for e in result.errors]}, status_code=400)

        return JSONResponse({"data": result.data})

    except Exception as e:
        return JSONResponse({"errors": [{"message": str(e)}]}, status_code=500)


@app.get("/graphql")
async def graphql_endpoint_get(request: Request):
    """Endpoint GraphQL via GET (aceita query como parâmetro)"""
    try:
        query = request.query_params.get("query")
        variables_str = request.query_params.get("variables")
        operation_name = request.query_params.get("operationName")

        if not query:
            return JSONResponse({"errors": [{"message": "Query não fornecida. Use ?query=..."}]}, status_code=400)

        variables = None
        if variables_str:
            import json
            try:
                variables = json.loads(variables_str)
            except json.JSONDecodeError:
                return JSONResponse({"errors": [{"message": "Variables inválidas (deve ser JSON)"}]}, status_code=400)

        result = schema.execute(
            query,
            variable_values=variables,
            operation_name=operation_name
        )

        if result.errors:
            return JSONResponse({"errors": [{"message": str(e)} for e in result.errors]}, status_code=400)

        return JSONResponse({"data": result.data})

    except Exception as e:
        return JSONResponse({"errors": [{"message": str(e)}]}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    print("🎵 Serviço GraphQL rodando na porta 3003")
    print("📍 Endpoint POST: http://localhost:3003/graphql")
    print("📍 Endpoint GET: http://localhost:3003/graphql?query={usuarios{id nome}}")
    uvicorn.run(app, host="0.0.0.0", port=3003)
