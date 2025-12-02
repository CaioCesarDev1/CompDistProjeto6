"""
Serviço SOAP implementado com Flask e processamento XML manual
"""
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import xml.etree.ElementTree as ET
from xml.dom import minidom
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

app = Flask(__name__)
CORS(app)

# Namespace SOAP
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
TNS_NS = "http://streaming-musicas.com/soap"

# Instância do repositório
db = SessionLocal()
repo = Repositorio(db)


def criar_resposta_soap(body_content):
    """Cria uma resposta SOAP válida"""
    envelope = ET.Element("soap:Envelope")
    envelope.set("xmlns:soap", SOAP_NS)
    envelope.set("xmlns:tns", TNS_NS)
    
    body = ET.SubElement(envelope, "soap:Body")
    body.append(body_content)
    
    return envelope


def criar_resposta_erro(mensagem):
    """Cria uma resposta SOAP de erro"""
    envelope = ET.Element("soap:Envelope")
    envelope.set("xmlns:soap", SOAP_NS)
    
    body = ET.SubElement(envelope, "soap:Body")
    fault = ET.SubElement(body, "soap:Fault")
    faultstring = ET.SubElement(fault, "faultstring")
    faultstring.text = mensagem
    
    return envelope


def xml_para_string(elemento):
    """Converte elemento XML para string formatada"""
    rough_string = ET.tostring(elemento, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


@app.route('/wsdl', methods=['GET'])
def wsdl():
    """Retorna o WSDL"""
    try:
        wsdl_path = os.path.join(os.path.dirname(__file__), 'wsdl.wsdl')
        with open(wsdl_path, 'r', encoding='utf-8') as f:
            wsdl_content = f.read()
        return Response(wsdl_content, mimetype='text/xml')
    except Exception as e:
        return f"Erro ao carregar WSDL: {str(e)}", 500


@app.route('/soap', methods=['POST'])
def soap_endpoint():
    """Endpoint SOAP principal"""
    try:
        # Parse do XML recebido
        root = ET.fromstring(request.data)
        
        # Encontra o body
        body = root.find(f".//{{{SOAP_NS}}}Body")
        if body is None:
            return Response(xml_para_string(criar_resposta_erro("Body SOAP não encontrado")), 
                          mimetype='text/xml'), 500
        
        # Pega o primeiro elemento filho (a operação)
        operacao = list(body)[0] if len(list(body)) > 0 else None
        if operacao is None:
            return Response(xml_para_string(criar_resposta_erro("Operação não encontrada")), 
                          mimetype='text/xml'), 500
        
        nome_operacao = operacao.tag.split('}')[-1] if '}' in operacao.tag else operacao.tag
        
        # Chama a função correspondente
        if nome_operacao in handlers:
            resposta = handlers[nome_operacao](operacao)
            return Response(xml_para_string(resposta), mimetype='text/xml')
        else:
            return Response(xml_para_string(criar_resposta_erro(f"Operação {nome_operacao} não encontrada")), 
                          mimetype='text/xml'), 500
            
    except ET.ParseError as e:
        return Response(xml_para_string(criar_resposta_erro(f"Erro ao parsear XML: {str(e)}")), 
                      mimetype='text/xml'), 500
    except Exception as e:
        return Response(xml_para_string(criar_resposta_erro(f"Erro: {str(e)}")), 
                      mimetype='text/xml'), 500


# Handlers para cada operação SOAP
def handler_criarUsuario(operacao):
    nome_elem = operacao.find('nome')
    idade_elem = operacao.find('idade')
    
    if nome_elem is None or idade_elem is None:
        return criar_resposta_erro("Nome e idade são obrigatórios")
    
    try:
        usuario = Usuario(
            id=str(uuid.uuid4()),
            nome=nome_elem.text,
            idade=int(idade_elem.text)
        )
        criado = repo.criar_usuario(usuario)
        
        resposta = ET.Element(f"{{{TNS_NS}}}criarUsuarioResponse")
        usuario_elem = ET.SubElement(resposta, "usuario")
        ET.SubElement(usuario_elem, "id").text = criado.id
        ET.SubElement(usuario_elem, "nome").text = criado.nome
        ET.SubElement(usuario_elem, "idade").text = str(criado.idade)
        
        return criar_resposta_soap(resposta)
    except Exception as e:
        return criar_resposta_erro(str(e))


def handler_obterUsuario(operacao):
    id_elem = operacao.find('id')
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    usuario = repo.obter_usuario(id_elem.text)
    if not usuario:
        return criar_resposta_erro("Usuário não encontrado")
    
    resposta = ET.Element(f"{{{TNS_NS}}}obterUsuarioResponse")
    usuario_elem = ET.SubElement(resposta, "usuario")
    ET.SubElement(usuario_elem, "id").text = usuario.id
    ET.SubElement(usuario_elem, "nome").text = usuario.nome
    ET.SubElement(usuario_elem, "idade").text = str(usuario.idade)
    
    return criar_resposta_soap(resposta)


def handler_listarUsuarios(operacao):
    usuarios = repo.listar_usuarios()
    
    resposta = ET.Element(f"{{{TNS_NS}}}listarUsuariosResponse")
    usuarios_elem = ET.SubElement(resposta, "usuarios")
    
    for u in usuarios:
        usuario_elem = ET.SubElement(usuarios_elem, "usuario")
        ET.SubElement(usuario_elem, "id").text = u.id
        ET.SubElement(usuario_elem, "nome").text = u.nome
        ET.SubElement(usuario_elem, "idade").text = str(u.idade)
    
    return criar_resposta_soap(resposta)


def handler_atualizarUsuario(operacao):
    id_elem = operacao.find('id')
    nome_elem = operacao.find('nome')
    idade_elem = operacao.find('idade')
    
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    dados = {}
    if nome_elem is not None:
        dados['nome'] = nome_elem.text
    if idade_elem is not None:
        dados['idade'] = int(idade_elem.text)
    
    usuario = repo.atualizar_usuario(id_elem.text, dados)
    if not usuario:
        return criar_resposta_erro("Usuário não encontrado")
    
    resposta = ET.Element(f"{{{TNS_NS}}}atualizarUsuarioResponse")
    usuario_elem = ET.SubElement(resposta, "usuario")
    ET.SubElement(usuario_elem, "id").text = usuario.id
    ET.SubElement(usuario_elem, "nome").text = usuario.nome
    ET.SubElement(usuario_elem, "idade").text = str(usuario.idade)
    
    return criar_resposta_soap(resposta)


def handler_removerUsuario(operacao):
    id_elem = operacao.find('id')
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    sucesso = repo.remover_usuario(id_elem.text)
    if not sucesso:
        return criar_resposta_erro("Usuário não encontrado")
    
    resposta = ET.Element(f"{{{TNS_NS}}}removerUsuarioResponse")
    ET.SubElement(resposta, "sucesso").text = "true"
    
    return criar_resposta_soap(resposta)


def handler_criarMusica(operacao):
    nome_elem = operacao.find('nome')
    artista_elem = operacao.find('artista')
    
    if nome_elem is None or artista_elem is None:
        return criar_resposta_erro("Nome e artista são obrigatórios")
    
    try:
        musica = Musica(
            id=str(uuid.uuid4()),
            nome=nome_elem.text,
            artista=artista_elem.text
        )
        criada = repo.criar_musica(musica)
        
        resposta = ET.Element(f"{{{TNS_NS}}}criarMusicaResponse")
        musica_elem = ET.SubElement(resposta, "musica")
        ET.SubElement(musica_elem, "id").text = criada.id
        ET.SubElement(musica_elem, "nome").text = criada.nome
        ET.SubElement(musica_elem, "artista").text = criada.artista
        
        return criar_resposta_soap(resposta)
    except Exception as e:
        return criar_resposta_erro(str(e))


def handler_obterMusica(operacao):
    id_elem = operacao.find('id')
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    musica = repo.obter_musica(id_elem.text)
    if not musica:
        return criar_resposta_erro("Música não encontrada")
    
    resposta = ET.Element(f"{{{TNS_NS}}}obterMusicaResponse")
    musica_elem = ET.SubElement(resposta, "musica")
    ET.SubElement(musica_elem, "id").text = musica.id
    ET.SubElement(musica_elem, "nome").text = musica.nome
    ET.SubElement(musica_elem, "artista").text = musica.artista
    
    return criar_resposta_soap(resposta)


def handler_listarMusicas(operacao):
    musicas = repo.listar_musicas()
    
    resposta = ET.Element(f"{{{TNS_NS}}}listarMusicasResponse")
    musicas_elem = ET.SubElement(resposta, "musicas")
    
    for m in musicas:
        musica_elem = ET.SubElement(musicas_elem, "musica")
        ET.SubElement(musica_elem, "id").text = m.id
        ET.SubElement(musica_elem, "nome").text = m.nome
        ET.SubElement(musica_elem, "artista").text = m.artista
    
    return criar_resposta_soap(resposta)


def handler_atualizarMusica(operacao):
    id_elem = operacao.find('id')
    nome_elem = operacao.find('nome')
    artista_elem = operacao.find('artista')
    
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    dados = {}
    if nome_elem is not None:
        dados['nome'] = nome_elem.text
    if artista_elem is not None:
        dados['artista'] = artista_elem.text
    
    musica = repo.atualizar_musica(id_elem.text, dados)
    if not musica:
        return criar_resposta_erro("Música não encontrada")
    
    resposta = ET.Element(f"{{{TNS_NS}}}atualizarMusicaResponse")
    musica_elem = ET.SubElement(resposta, "musica")
    ET.SubElement(musica_elem, "id").text = musica.id
    ET.SubElement(musica_elem, "nome").text = musica.nome
    ET.SubElement(musica_elem, "artista").text = musica.artista
    
    return criar_resposta_soap(resposta)


def handler_removerMusica(operacao):
    id_elem = operacao.find('id')
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    sucesso = repo.remover_musica(id_elem.text)
    if not sucesso:
        return criar_resposta_erro("Música não encontrada")
    
    resposta = ET.Element(f"{{{TNS_NS}}}removerMusicaResponse")
    ET.SubElement(resposta, "sucesso").text = "true"
    
    return criar_resposta_soap(resposta)


def handler_criarPlaylist(operacao):
    nome_elem = operacao.find('nome')
    usuarioId_elem = operacao.find('usuarioId')
    
    if nome_elem is None or usuarioId_elem is None:
        return criar_resposta_erro("Nome e usuarioId são obrigatórios")
    
    try:
        playlist = Playlist(
            id=str(uuid.uuid4()),
            nome=nome_elem.text,
            usuario_id=usuarioId_elem.text,
            musicas_ids=[]
        )
        criada = repo.criar_playlist(playlist)
        
        resposta = ET.Element(f"{{{TNS_NS}}}criarPlaylistResponse")
        playlist_elem = ET.SubElement(resposta, "playlist")
        ET.SubElement(playlist_elem, "id").text = criada.id
        ET.SubElement(playlist_elem, "nome").text = criada.nome
        ET.SubElement(playlist_elem, "usuarioId").text = criada.usuario_id
        musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
        for mid in criada.musicas_ids:
            ET.SubElement(musicasIds_elem, "item").text = mid
        
        return criar_resposta_soap(resposta)
    except Exception as e:
        return criar_resposta_erro(str(e))


def handler_obterPlaylist(operacao):
    id_elem = operacao.find('id')
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    playlist = repo.obter_playlist(id_elem.text)
    if not playlist:
        return criar_resposta_erro("Playlist não encontrada")
    
    resposta = ET.Element(f"{{{TNS_NS}}}obterPlaylistResponse")
    playlist_elem = ET.SubElement(resposta, "playlist")
    ET.SubElement(playlist_elem, "id").text = playlist.id
    ET.SubElement(playlist_elem, "nome").text = playlist.nome
    ET.SubElement(playlist_elem, "usuarioId").text = playlist.usuario_id
    musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
    for mid in playlist.musicas_ids:
        ET.SubElement(musicasIds_elem, "item").text = mid
    
    return criar_resposta_soap(resposta)


def handler_listarPlaylists(operacao):
    playlists = repo.listar_playlists()
    
    resposta = ET.Element(f"{{{TNS_NS}}}listarPlaylistsResponse")
    playlists_elem = ET.SubElement(resposta, "playlists")
    
    for p in playlists:
        playlist_elem = ET.SubElement(playlists_elem, "playlist")
        ET.SubElement(playlist_elem, "id").text = p.id
        ET.SubElement(playlist_elem, "nome").text = p.nome
        ET.SubElement(playlist_elem, "usuarioId").text = p.usuario_id
        musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
        for mid in p.musicas_ids:
            ET.SubElement(musicasIds_elem, "item").text = mid
    
    return criar_resposta_soap(resposta)


def handler_listarPlaylistsPorUsuario(operacao):
    usuarioId_elem = operacao.find('usuarioId')
    if usuarioId_elem is None:
        return criar_resposta_erro("usuarioId é obrigatório")
    
    playlists = repo.listar_playlists_por_usuario(usuarioId_elem.text)
    
    resposta = ET.Element(f"{{{TNS_NS}}}listarPlaylistsPorUsuarioResponse")
    playlists_elem = ET.SubElement(resposta, "playlists")
    
    for p in playlists:
        playlist_elem = ET.SubElement(playlists_elem, "playlist")
        ET.SubElement(playlist_elem, "id").text = p.id
        ET.SubElement(playlist_elem, "nome").text = p.nome
        ET.SubElement(playlist_elem, "usuarioId").text = p.usuario_id
        musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
        for mid in p.musicas_ids:
            ET.SubElement(musicasIds_elem, "item").text = mid
    
    return criar_resposta_soap(resposta)


def handler_listarMusicasPorPlaylist(operacao):
    playlistId_elem = operacao.find('playlistId')
    if playlistId_elem is None:
        return criar_resposta_erro("playlistId é obrigatório")
    
    musicas = repo.listar_musicas_por_playlist(playlistId_elem.text)
    
    resposta = ET.Element(f"{{{TNS_NS}}}listarMusicasPorPlaylistResponse")
    musicas_elem = ET.SubElement(resposta, "musicas")
    
    for m in musicas:
        musica_elem = ET.SubElement(musicas_elem, "musica")
        ET.SubElement(musica_elem, "id").text = m.id
        ET.SubElement(musica_elem, "nome").text = m.nome
        ET.SubElement(musica_elem, "artista").text = m.artista
    
    return criar_resposta_soap(resposta)


def handler_listarPlaylistsPorMusica(operacao):
    musicaId_elem = operacao.find('musicaId')
    if musicaId_elem is None:
        return criar_resposta_erro("musicaId é obrigatório")
    
    playlists = repo.listar_playlists_por_musica(musicaId_elem.text)
    
    resposta = ET.Element(f"{{{TNS_NS}}}listarPlaylistsPorMusicaResponse")
    playlists_elem = ET.SubElement(resposta, "playlists")
    
    for p in playlists:
        playlist_elem = ET.SubElement(playlists_elem, "playlist")
        ET.SubElement(playlist_elem, "id").text = p.id
        ET.SubElement(playlist_elem, "nome").text = p.nome
        ET.SubElement(playlist_elem, "usuarioId").text = p.usuario_id
        musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
        for mid in p.musicas_ids:
            ET.SubElement(musicasIds_elem, "item").text = mid
    
    return criar_resposta_soap(resposta)


def handler_atualizarPlaylist(operacao):
    id_elem = operacao.find('id')
    nome_elem = operacao.find('nome')
    usuarioId_elem = operacao.find('usuarioId')
    
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    dados = {}
    if nome_elem is not None:
        dados['nome'] = nome_elem.text
    if usuarioId_elem is not None:
        dados['usuario_id'] = usuarioId_elem.text
    
    try:
        playlist = repo.atualizar_playlist(id_elem.text, dados)
        if not playlist:
            return criar_resposta_erro("Playlist não encontrada")
        
        resposta = ET.Element(f"{{{TNS_NS}}}atualizarPlaylistResponse")
        playlist_elem = ET.SubElement(resposta, "playlist")
        ET.SubElement(playlist_elem, "id").text = playlist.id
        ET.SubElement(playlist_elem, "nome").text = playlist.nome
        ET.SubElement(playlist_elem, "usuarioId").text = playlist.usuario_id
        musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
        for mid in playlist.musicas_ids:
            ET.SubElement(musicasIds_elem, "item").text = mid
        
        return criar_resposta_soap(resposta)
    except Exception as e:
        return criar_resposta_erro(str(e))


def handler_adicionarMusicaAPlaylist(operacao):
    playlistId_elem = operacao.find('playlistId')
    musicaId_elem = operacao.find('musicaId')
    
    if playlistId_elem is None or musicaId_elem is None:
        return criar_resposta_erro("playlistId e musicaId são obrigatórios")
    
    try:
        playlist = repo.adicionar_musica_a_playlist(playlistId_elem.text, musicaId_elem.text)
        if not playlist:
            return criar_resposta_erro("Playlist não encontrada")
        
        resposta = ET.Element(f"{{{TNS_NS}}}adicionarMusicaAPlaylistResponse")
        playlist_elem = ET.SubElement(resposta, "playlist")
        ET.SubElement(playlist_elem, "id").text = playlist.id
        ET.SubElement(playlist_elem, "nome").text = playlist.nome
        ET.SubElement(playlist_elem, "usuarioId").text = playlist.usuario_id
        musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
        for mid in playlist.musicas_ids:
            ET.SubElement(musicasIds_elem, "item").text = mid
        
        return criar_resposta_soap(resposta)
    except Exception as e:
        return criar_resposta_erro(str(e))


def handler_removerMusicaDePlaylist(operacao):
    playlistId_elem = operacao.find('playlistId')
    musicaId_elem = operacao.find('musicaId')
    
    if playlistId_elem is None or musicaId_elem is None:
        return criar_resposta_erro("playlistId e musicaId são obrigatórios")
    
    playlist = repo.remover_musica_de_playlist(playlistId_elem.text, musicaId_elem.text)
    if not playlist:
        return criar_resposta_erro("Playlist não encontrada")
    
    resposta = ET.Element(f"{{{TNS_NS}}}removerMusicaDePlaylistResponse")
    playlist_elem = ET.SubElement(resposta, "playlist")
    ET.SubElement(playlist_elem, "id").text = playlist.id
    ET.SubElement(playlist_elem, "nome").text = playlist.nome
    ET.SubElement(playlist_elem, "usuarioId").text = playlist.usuario_id
    musicasIds_elem = ET.SubElement(playlist_elem, "musicasIds")
    for mid in playlist.musicas_ids:
        ET.SubElement(musicasIds_elem, "item").text = mid
    
    return criar_resposta_soap(resposta)


def handler_removerPlaylist(operacao):
    id_elem = operacao.find('id')
    if id_elem is None:
        return criar_resposta_erro("ID é obrigatório")
    
    sucesso = repo.remover_playlist(id_elem.text)
    if not sucesso:
        return criar_resposta_erro("Playlist não encontrada")
    
    resposta = ET.Element(f"{{{TNS_NS}}}removerPlaylistResponse")
    ET.SubElement(resposta, "sucesso").text = "true"
    
    return criar_resposta_soap(resposta)


# Mapeamento de operações para handlers
handlers = {
    'criarUsuario': handler_criarUsuario,
    'obterUsuario': handler_obterUsuario,
    'listarUsuarios': handler_listarUsuarios,
    'atualizarUsuario': handler_atualizarUsuario,
    'removerUsuario': handler_removerUsuario,
    'criarMusica': handler_criarMusica,
    'obterMusica': handler_obterMusica,
    'listarMusicas': handler_listarMusicas,
    'atualizarMusica': handler_atualizarMusica,
    'removerMusica': handler_removerMusica,
    'criarPlaylist': handler_criarPlaylist,
    'obterPlaylist': handler_obterPlaylist,
    'listarPlaylists': handler_listarPlaylists,
    'listarPlaylistsPorUsuario': handler_listarPlaylistsPorUsuario,
    'listarMusicasPorPlaylist': handler_listarMusicasPorPlaylist,
    'listarPlaylistsPorMusica': handler_listarPlaylistsPorMusica,
    'atualizarPlaylist': handler_atualizarPlaylist,
    'adicionarMusicaAPlaylist': handler_adicionarMusicaAPlaylist,
    'removerMusicaDePlaylist': handler_removerMusicaDePlaylist,
    'removerPlaylist': handler_removerPlaylist,
}


def soap_response_to_json(soap_response):
    """Converte uma resposta SOAP para JSON"""
    try:
        # Extrai o body da resposta SOAP
        body = soap_response.find(f".//{{{SOAP_NS}}}Body")
        if body is None:
            return {"error": "Resposta SOAP inválida - Body não encontrado"}
        
        # Pega o primeiro elemento filho (a operação de resposta)
        response_elem = list(body)[0] if len(list(body)) > 0 else None
        if response_elem is None:
            return {"error": "Resposta SOAP inválida - Conteúdo não encontrado"}
        
        # Converte para JSON
        def element_to_dict(elem):
            if len(elem) == 0:
                return elem.text if elem.text else ""
            
            # Se todos os filhos têm o mesmo nome, é uma lista
            children_tags = [child.tag.split('}')[-1] if '}' in child.tag else child.tag for child in elem]
            if len(children_tags) > 1 and len(set(children_tags)) == 1:
                # É uma lista - retorna array de objetos
                return [element_to_dict(child) for child in elem]
            
            # É um objeto - retorna dict
            result = {}
            for child in elem:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if len(child) == 0:
                    result[tag_name] = child.text if child.text else ""
                else:
                    child_dict = element_to_dict(child)
                    # Se já existe e não é lista, converte para lista
                    if tag_name in result:
                        if not isinstance(result[tag_name], list):
                            result[tag_name] = [result[tag_name]]
                        result[tag_name].append(child_dict)
                    else:
                        result[tag_name] = child_dict
            
            return result
        
        return element_to_dict(response_elem)
    except Exception as e:
        return {"error": f"Erro ao converter resposta SOAP: {str(e)}"}


@app.route('/api/usuarios', methods=['GET'])
def get_listar_usuarios():
    """Endpoint GET para listar usuários (retorna JSON)"""
    try:
        # Cria um elemento vazio para o handler (já que não precisa de parâmetros)
        dummy_operation = ET.Element("listarUsuarios")
        soap_response = handler_listarUsuarios(dummy_operation)
        json_response = soap_response_to_json(soap_response)
        return jsonify(json_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/musicas', methods=['GET'])
def get_listar_musicas():
    """Endpoint GET para listar músicas (retorna JSON)"""
    try:
        dummy_operation = ET.Element("listarMusicas")
        soap_response = handler_listarMusicas(dummy_operation)
        json_response = soap_response_to_json(soap_response)
        return jsonify(json_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/playlists', methods=['GET'])
def get_listar_playlists():
    """Endpoint GET para listar playlists (retorna JSON)"""
    try:
        dummy_operation = ET.Element("listarPlaylists")
        soap_response = handler_listarPlaylists(dummy_operation)
        json_response = soap_response_to_json(soap_response)
        return jsonify(json_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    PORT = 3002
    print(f"Serviço SOAP rodando na porta {PORT}")
    print(f"WSDL disponível em: http://localhost:{PORT}/wsdl")
    print(f"Endpoint SOAP: http://localhost:{PORT}/soap")
    app.run(host='0.0.0.0', port=PORT, debug=False)
