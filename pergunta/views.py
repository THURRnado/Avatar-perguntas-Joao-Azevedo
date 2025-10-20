from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pergunta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests


def home(request):
    pergunta = Pergunta.objects.filter(ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero':'todos'})


def filtro_genero(request, genero):
    pergunta = Pergunta.objects.filter(genero=genero ,ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero':genero})


def escolher(request, pk):
    pergunta = Pergunta.objects.get(pk=pk)
    texto = pergunta.texto
    print(f"[Django] Pergunta escolhida: {texto}")

    # Armazena na sessão para confirmação posterior
    request.session['pergunta_confirmar'] = texto

    # Envia para Flask para que o avatar pergunte a confirmação
    try:
        response = requests.post(
            "http://localhost:5000/falar",
            json={"texto": texto},
            timeout=5
        )
        if response.status_code != 200:
            messages.error(request, "Erro ao enviar para o avatar.")
    except requests.exceptions.RequestException as e:
        print(f"[Django] Erro ao conectar com Flask: {e}")
        messages.error(request, "Não foi possível se comunicar com o avatar.")

    # Renderiza página de confirmação
    return render(request, 'pergunta/confirmacao.html', {'pergunta': texto})


def confirmar_pergunta(request):
    if request.method == "POST":
        resposta = request.POST.get("resposta")
        pergunta = request.session.get("pergunta_confirmar")

        if not pergunta:
            messages.error(request, "Não há pergunta para confirmar.")
            return redirect('home')

        if resposta == "sim":
            # Envia a pergunta final para o Flask
            try:
                response = requests.post(
                    "http://localhost:5000/falar_final",
                    json={"texto": pergunta},
                    timeout=5
                )
                if response.status_code == 200:
                    messages.success(request, "Pergunta enviada ao avatar com sucesso!")
                else:
                    messages.error(request, f"Erro ao enviar ao avatar: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[Django] Erro ao conectar com Flask: {e}")
                messages.error(request, "Não foi possível se comunicar com o avatar.")

        # Limpa a sessão
        request.session.pop('pergunta_confirmar', None)
        return redirect('home')


@csrf_exempt
def avatar_retorno(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mensagem = data.get("mensagem", "")
        print(f"[Django] Retorno do Flask: {mensagem}")
        # Aqui você pode atualizar o banco, enviar WebSocket, etc.
        return JsonResponse({"status": "ok"})
    return JsonResponse({"erro": "Método não permitido"}, status=405)