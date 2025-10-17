from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pergunta


def home(request):
    pergunta = Pergunta.objects.filter(ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero':'todos'})


def filtro_genero(request, genero):
    pergunta = Pergunta.objects.filter(genero=genero ,ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero':genero})


def escolher(request, pk):
    pergunta = Pergunta.objects.get(pk=pk)
    print(pergunta.texto)

    messages.success(request, "Operação realizada com sucesso!")

    return redirect('home')