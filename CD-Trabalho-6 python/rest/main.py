"""
Serviço REST implementado com FastAPI
"""
import sys
import os
import importlib.util

# SOLUÇÃO ALTERNATIVA: Importa diretamente dos arquivos sem usar sys.path
# Obtém o diretório absoluto do arquivo atualS
current_file = os.path.abspath(__file__)
# Obtém o diretório pai (rest/) e depois o pai dele (raiz do projeto)
root_dir = os.path.dirname(os.path.dirname(current_file))
root_dir = os.path.normpath(os.path.abspath(root_dir))

# Caminho para o diretório shared
shared_dir = os.path.join(root_dir, 'shared')

# Verifica se existe
if not os.path.exists(shared_dir):
    print(f"ERRO: Diretório 'shared' não encontrado em: {root_dir}")
    print(f"Arquivo atual: {current_file}")
    sys.exit(1)

# Adiciona o diretório raiz ao sys.path (método tradicional)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Cria o pacote shared primeiro
shared_init = os.path.join(shared_dir, '__init__.py')
if os.path.exists(shared_init):
    spec = importlib.util.spec_from_file_location("shared", shared_init)
    if spec and spec.loader:
        shared_pkg = importlib.util.module_from_spec(spec)
        sys.modules['shared'] = shared_pkg
        spec.loader.exec_module(shared_pkg)

# Importa os módulos compartilhados diretamente dos arquivos
def load_module(module_name, file_path):
    """Carrega um módulo diretamente de um arquivo"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {module_name} de {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Carrega os módulos compartilhados na ordem correta (respeitando dependências)
try:
    # Primeiro carrega models (não tem dependências de outros módulos shared)
    models_file = os.path.join(shared_dir, 'models.py')
    if not os.path.exists(models_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {models_file}")
    load_module('shared.models', models_file)
    
    # Depois carrega database (depende de models)
    database_file = os.path.join(shared_dir, 'database.py')
    if not os.path.exists(database_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {database_file}")
    load_module('shared.database', database_file)
    
    # Por último carrega repository (depende de models e database)
    repository_file = os.path.join(shared_dir, 'repository.py')
    if not os.path.exists(repository_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {repository_file}")
    load_module('shared.repository', repository_file)
    
except Exception as e:
    print(f"ERRO ao carregar módulos compartilhados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Agora importa normalmente (os módulos já estão em sys.modules)
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from shared.database import get_db, init_db
from shared.repository import Repositorio
from shared.models import Usuario, Musica, Playlist

app = FastAPI(title="Streaming de Músicas - REST API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa o banco de dados na primeira execução
@app.on_event("startup")
async def startup_event():
    init_db()


def get_repositorio(db: Session = Depends(get_db)) -> Repositorio:
    """Dependency para obter o repositório"""
    return Repositorio(db)




# ========== USUÁRIOS ==========

@app.post("/api/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(usuario: Usuario, repo: Repositorio = Depends(get_repositorio)):
    """Cria um novo usuário"""
    try:
        return repo.criar_usuario(usuario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/usuarios", response_model=List[Usuario])
def listar_usuarios(repo: Repositorio = Depends(get_repositorio)):
    """Lista todos os usuários"""
    try:
        return repo.listar_usuarios()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@app.get("/api/usuarios/{id}", response_model=Usuario)
def obter_usuario(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Obtém um usuário por ID"""
    usuario = repo.obter_usuario(id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.put("/api/usuarios/{id}", response_model=Usuario)
def atualizar_usuario(id: str, dados: dict, repo: Repositorio = Depends(get_repositorio)):
    """Atualiza um usuário"""
    usuario = repo.atualizar_usuario(id, dados)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.delete("/api/usuarios/{id}", status_code=204)
def remover_usuario(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Remove um usuário"""
    if not repo.remover_usuario(id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")


# ========== MÚSICAS ==========

@app.post("/api/musicas", response_model=Musica, status_code=201)
def criar_musica(musica: Musica, repo: Repositorio = Depends(get_repositorio)):
    """Cria uma nova música"""
    try:
        return repo.criar_musica(musica)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/musicas", response_model=List[Musica])
def listar_musicas(repo: Repositorio = Depends(get_repositorio)):
    """Lista todas as músicas"""
    try:
        return repo.listar_musicas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/musicas/{id}", response_model=Musica)
def obter_musica(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Obtém uma música por ID"""
    musica = repo.obter_musica(id)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    return musica


@app.put("/api/musicas/{id}", response_model=Musica)
def atualizar_musica(id: str, dados: dict, repo: Repositorio = Depends(get_repositorio)):
    """Atualiza uma música"""
    musica = repo.atualizar_musica(id, dados)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    return musica


@app.delete("/api/musicas/{id}", status_code=204)
def remover_musica(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Remove uma música"""
    if not repo.remover_musica(id):
        raise HTTPException(status_code=404, detail="Música não encontrada")


# ========== PLAYLISTS ==========

@app.post("/api/playlists", response_model=Playlist, status_code=201)
async def criar_playlist(request: Request, repo: Repositorio = Depends(get_repositorio)):
    """Cria uma nova playlist"""
    try:
        # Pega o body da requisição
        body = await request.json()
        
        # Extrai e valida campos do body
        nome = body.get("nome")
        usuario_id = body.get("usuarioId") or body.get("usuario_id")
        musicas_ids = body.get("musicasIds") or body.get("musicas_ids") or []
        
        # Validação manual
        if not nome:
            raise HTTPException(status_code=400, detail="nome é obrigatório")
        if not usuario_id:
            raise HTTPException(status_code=400, detail="usuarioId é obrigatório")
        
        # Cria objeto Playlist
        playlist = Playlist(
            nome=nome,
            usuario_id=usuario_id,
            musicas_ids=musicas_ids
        )
        
        # Chama o repositório
        resultado = repo.criar_playlist(playlist)
        return resultado
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao criar playlist: {str(e)}")


@app.get("/api/playlists", response_model=List[Playlist])
def listar_playlists(repo: Repositorio = Depends(get_repositorio)):
    """Lista todas as playlists"""
    try:
        return repo.listar_playlists()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao listar playlists: {str(e)}")


@app.get("/api/playlists/{id}", response_model=Playlist)
def obter_playlist(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Obtém uma playlist por ID"""
    playlist = repo.obter_playlist(id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return playlist


@app.get("/api/usuarios/{usuario_id}/playlists", response_model=List[Playlist])
def listar_playlists_por_usuario(usuario_id: str, repo: Repositorio = Depends(get_repositorio)):
    """Lista playlists de um usuário"""
    try:
        return repo.listar_playlists_por_usuario(usuario_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/playlists/{id}/musicas", response_model=List[Musica])
def listar_musicas_por_playlist(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Lista músicas de uma playlist"""
    try:
        return repo.listar_musicas_por_playlist(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/musicas/{musica_id}/playlists", response_model=List[Playlist])
def listar_playlists_por_musica(musica_id: str, repo: Repositorio = Depends(get_repositorio)):
    """Lista playlists que contêm uma música"""
    try:
        return repo.listar_playlists_por_musica(musica_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/playlists/{id}", response_model=Playlist)
def atualizar_playlist(id: str, dados: dict, repo: Repositorio = Depends(get_repositorio)):
    """Atualiza uma playlist"""
    try:
        playlist = repo.atualizar_playlist(id, dados)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist não encontrada")
        return playlist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/playlists/{id}/musicas", response_model=Playlist)
def adicionar_musica_a_playlist(id: str, body: dict, repo: Repositorio = Depends(get_repositorio)):
    """Adiciona uma música a uma playlist"""
    try:
        musica_id = body.get("musicaId")
        if not musica_id:
            raise HTTPException(status_code=400, detail="musicaId é obrigatório")
        playlist = repo.adicionar_musica_a_playlist(id, musica_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist não encontrada")
        return playlist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/playlists/{id}/musicas/{musica_id}", response_model=Playlist)
def remover_musica_de_playlist(id: str, musica_id: str, repo: Repositorio = Depends(get_repositorio)):
    """Remove uma música de uma playlist"""
    playlist = repo.remover_musica_de_playlist(id, musica_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return playlist


@app.delete("/api/playlists/{id}", status_code=204)
def remover_playlist(id: str, repo: Repositorio = Depends(get_repositorio)):
    """Remove uma playlist"""
    if not repo.remover_playlist(id):
        raise HTTPException(status_code=404, detail="Playlist não encontrada")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

