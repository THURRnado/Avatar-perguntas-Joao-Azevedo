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

    request.session['pergunta_confirmar'] = texto

    try:
        response = requests.post(
            "http://localhost:5000/escolha",
            json={"texto": texto},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return render(request, 'pergunta/confirmacao.html', {'pergunta': texto})
            else:
                messages.error(request, "O avatar não confirmou a pergunta.")
        else:
            messages.error(request, f"Erro no avatar: status {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[Django] Erro ao conectar com Flask: {e}")
        messages.error(request, "Não foi possível se comunicar com o avatar.")

    return redirect('home')


def confirmar_pergunta(request):
    if request.method == "POST":
        resposta = request.POST.get("resposta")
        pergunta = request.session.get("pergunta_confirmar")

        if not pergunta:
            messages.error(request, "Não há pergunta para confirmar.")
            return redirect('home')

        if resposta == "sim":
            try:
                response = requests.post(
                    "http://localhost:5000/responder",
                    json={"texto": pergunta},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        return redirect('home')
                    else:
                        messages.error(request, "O avatar não confirmou a pergunta.")
                else:
                    messages.error(request, f"Erro ao enviar ao avatar: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[Django] Erro ao conectar com Flask: {e}")
                messages.error(request, "Não foi possível se comunicar com o avatar.")

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