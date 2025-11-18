import os
import json
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pergunta
import requests

IA_OUTPUT_DIR = os.getenv('IA_OUTPUT_DIR')
IA_INPUT_DIR = os.getenv('IA_INPUT_DIR')


def home(request):
    pergunta = Pergunta.objects.filter(ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero': 'todos'})



def filtro_genero(request, genero):
    pergunta = Pergunta.objects.filter(genero=genero, ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero': genero})



def escolher(request, pk):
    pergunta = Pergunta.objects.get(pk=pk)
    texto = pergunta.texto
    print(f"[Django] Pergunta escolhida: {texto}")

    request.session['pergunta_confirmar'] = texto

    try:
        # Envia para o Avatar (Flask) apenas para ele FALAR a pergunta
        response = requests.post(
            os.getenv('URL_AVATAR_ESCOLHA'),
            json={"texto": texto},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                # Avatar falou com sucesso → mostra tela de confirmação (sim/não)
                return render(request, 'pergunta/confirmacao.html', {'pergunta': texto})
            else:
                messages.error(request, "O avatar não confirmou a pergunta.")
        else:
            messages.error(request, f"Erro no avatar: status {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[Django] Erro ao conectar com Flask: {e}")
        messages.error(request, "Não foi possível se comunicar com o avatar.")

    return redirect('home')



def comunicacao_ia(request):
    """
    Após o usuário clicar em "Sim" ou "Não":
      - Se "Sim": cria o arquivo JSON e inicia a comunicação com o backend_ia.
      - Se "Não": apenas limpa a sessão e retorna à tela inicial.
    """
    if request.method != "POST":
        return redirect('home')

    resposta = request.POST.get("resposta")
    pergunta = request.session.get("pergunta_confirmar")

    if not pergunta:
        messages.error(request, "Nenhuma pergunta pendente para confirmar.")
        return redirect('home')

    # Caso o usuário diga "não", simplesmente volta à home
    if resposta == "nao":
        print("[Django] Usuário respondeu NÃO — cancelando comunicação com IA.")
        request.session.pop('pergunta_confirmar', None)
        messages.info(request, "Pergunta cancelada pelo usuário.")
        return redirect('home')

    # Se chegou aqui, a resposta foi "sim"
    pergunta_json_path = os.path.join(IA_INPUT_DIR, "pergunta.json")
    signal_path = os.path.join(IA_INPUT_DIR, "ASK_TEXT.signal")

    # Cria o arquivo JSON para o backend_ia
    with open(pergunta_json_path, "w", encoding="utf-8") as f:
        json.dump({"texto": pergunta}, f, ensure_ascii=False, indent=4)

    with open(signal_path, "w", encoding="utf-8") as f:
        f.write("READY") 

    print(f"[Django] Arquivo JSON criado: {pergunta_json_path}")

    return redirect('confirmar_pergunta')



def confirmar_pergunta(request):
    """
    Monitora a pasta até o backend_ia gerar READY_AVATAR.signal.
    Quando o sinal é detectado, lê os arquivos e envia a pergunta ao avatar para resposta final.
    """
    print("[Django] Aguardando READY_AVATAR.signal...")

    signal_path = os.path.join(IA_OUTPUT_DIR, "READY_AVATAR.signal")
    resposta_json_path = os.path.join(IA_OUTPUT_DIR, "resposta.json")

    timeout = 60
    start_time = time.time()

    while not os.path.exists(signal_path):
        time.sleep(1)
        if time.time() - start_time > timeout:
            print("[Django] Timeout: nenhum READY_AVATAR.signal detectado.")
            messages.error(request, "A IA não respondeu a tempo.")
            return redirect('home')

    print("[Django] Sinal detectado! Lendo arquivos gerados...")

    try:
        with open(resposta_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            resposta = data.get("texto", "resposta desconhecida")

        # Lê arquivos de áudio (resposta)
        #wav_files = [f for f in os.listdir(IA_OUTPUT_DIR) if f.endswith(".wav")]
        #print(f"[Django] Arquivos de áudio: {wav_files}")

        # Chama o avatar para tocar/falar a resposta final
        response = requests.post(
            os.getenv('URL_AVATAR_RESPONDER'),
            json={"texto": resposta},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("[Django] Avatar respondeu com sucesso.")
            else:
                messages.error(request, "O avatar não confirmou a resposta.")
        else:
            messages.error(request, f"Erro no avatar: {response.text}")

    except Exception as e:
        print(f"[Django] Erro ao processar resposta: {e}")
        messages.error(request, "Erro ao processar resposta do backend_ia.")

    finally:
        # Remove o sinal para o próximo ciclo
        if os.path.exists(signal_path):
            os.remove(signal_path)
            print("[Django] Sinal removido.")

        if os.path.exists(resposta_json_path):
            os.remove(resposta_json_path)
            print("[Django] Pergunta removida.")

    # Limpa a sessão
    request.session.pop('pergunta_confirmar', None)
    return redirect('home')



@csrf_exempt
def avatar_retorno(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mensagem = data.get("mensagem", "")
        print(f"[Django] Retorno do Flask: {mensagem}")
        return JsonResponse({"status": "ok"})
    return JsonResponse({"erro": "Método não permitido"}, status=405)