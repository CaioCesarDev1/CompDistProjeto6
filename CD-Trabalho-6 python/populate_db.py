"""
Script para popular o banco de dados com milhares de dados
Execute após criar o banco: python populate_db.py
"""
import sys
import os
import random
import uuid
from faker import Faker

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from shared.database import init_db, SessionLocal
from shared.repository import Repositorio
from shared.models import Usuario, Musica, Playlist

# Inicializa Faker para gerar dados realistas
fake = Faker('pt_BR')

# Configurações
NUM_USUARIOS = 5000
NUM_MUSICAS = 10000
NUM_PLAYLISTS = 2000
MIN_MUSICAS_POR_PLAYLIST = 3
MAX_MUSICAS_POR_PLAYLIST = 20  # Reduzido para melhor performance


def gerar_nome_musica():
    """Gera um nome de música realista"""
    tipos = [
        f"{fake.word().title()} {fake.word()}",
        f"{fake.word().title()}",
        f"{fake.word().title()} {fake.word()} {fake.word()}",
        f"{fake.word().title()} de {fake.word().title()}",
    ]
    return random.choice(tipos)


def gerar_nome_artista():
    """Gera um nome de artista realista"""
    tipos = [
        f"{fake.first_name()} {fake.last_name()}",
        f"{fake.word().title()} {fake.word().title()}",
        f"{fake.first_name()}",
        f"The {fake.word().title()}",
    ]
    return random.choice(tipos)


def popular_banco():
    """Popula o banco de dados com dados de teste"""
    print("🎵 Iniciando população do banco de dados...")
    
    # Inicializa o banco
    init_db()
    
    # Cria sessão
    db = SessionLocal()
    repo = Repositorio(db)
    
    try:
        # ========== CRIAR USUÁRIOS ==========
        print(f"\n📝 Criando {NUM_USUARIOS} usuários...")
        usuarios_ids = []
        for i in range(NUM_USUARIOS):
            usuario = Usuario(
                id=str(uuid.uuid4()),
                nome=fake.name(),
                idade=random.randint(13, 80)
            )
            try:
                criado = repo.criar_usuario(usuario)
                usuarios_ids.append(criado.id)
                if (i + 1) % 500 == 0:
                    print(f"  ✓ {i + 1}/{NUM_USUARIOS} usuários criados")
            except Exception as e:
                print(f"  ⚠ Erro ao criar usuário {i + 1}: {e}")
        
        print(f"✅ {len(usuarios_ids)} usuários criados com sucesso!")
        
        # ========== CRIAR MÚSICAS ==========
        print(f"\n🎶 Criando {NUM_MUSICAS} músicas...")
        musicas_ids = []
        for i in range(NUM_MUSICAS):
            musica = Musica(
                id=str(uuid.uuid4()),
                nome=gerar_nome_musica(),
                artista=gerar_nome_artista()
            )
            try:
                criada = repo.criar_musica(musica)
                musicas_ids.append(criada.id)
                if (i + 1) % 1000 == 0:
                    print(f"  ✓ {i + 1}/{NUM_MUSICAS} músicas criadas")
            except Exception as e:
                print(f"  ⚠ Erro ao criar música {i + 1}: {e}")
        
        print(f"✅ {len(musicas_ids)} músicas criadas com sucesso!")
        
        # ========== CRIAR PLAYLISTS COM MÚSICAS ==========
        print(f"\n📋 Criando {NUM_PLAYLISTS} playlists (com músicas)...")
        playlists_ids = []
        total_adicoes = 0
        
        for i in range(NUM_PLAYLISTS):
            # Seleciona um usuário aleatório
            usuario_id = random.choice(usuarios_ids)
            
            # Número aleatório de músicas por playlist
            num_musicas = random.randint(MIN_MUSICAS_POR_PLAYLIST, MAX_MUSICAS_POR_PLAYLIST)
            
            # Seleciona músicas aleatórias (sem repetição)
            musicas_selecionadas = random.sample(musicas_ids, min(num_musicas, len(musicas_ids)))
            
            playlist = Playlist(
                id=str(uuid.uuid4()),
                nome=f"{fake.word().title()} {fake.word().title()}",
                usuario_id=usuario_id,
                musicas_ids=musicas_selecionadas  # Cria já com as músicas
            )
            try:
                criada = repo.criar_playlist(playlist)
                playlists_ids.append(criada.id)
                total_adicoes += len(musicas_selecionadas)
                
                if (i + 1) % 200 == 0:
                    print(f"  ✓ {i + 1}/{NUM_PLAYLISTS} playlists criadas ({total_adicoes} músicas adicionadas)")
            except Exception as e:
                print(f"  ⚠ Erro ao criar playlist {i + 1}: {e}")
        
        print(f"✅ {len(playlists_ids)} playlists criadas com sucesso!")
        print(f"✅ {total_adicoes} músicas adicionadas às playlists!")
        
        # ========== RESUMO ==========
        print("\n" + "="*50)
        print("📊 RESUMO DA POPULAÇÃO:")
        print("="*50)
        print(f"  👥 Usuários: {len(usuarios_ids)}")
        print(f"  🎶 Músicas: {len(musicas_ids)}")
        print(f"  📋 Playlists: {len(playlists_ids)}")
        print(f"  🎵 Músicas em playlists: {total_adicoes}")
        print("="*50)
        print("✅ Banco de dados populado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    popular_banco()

