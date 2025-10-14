from django.shortcuts import render
from .models import Pergunta


def home(request):
    pergunta = Pergunta.objects.filter(ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero':'todos'})


def filtro_genero(request, genero):
    pergunta = Pergunta.objects.filter(genero=genero ,ativo=True).order_by('-vezes_respondida')
    return render(request, 'pergunta/index.html', {'pergunta': pergunta, 'genero':genero})