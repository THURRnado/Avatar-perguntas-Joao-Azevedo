from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Pergunta

@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('texto_resumido', 'genero', 'vezes_respondida', 'ativo', 'criado_em', 'modificado_em')

    list_display_links = ('texto_resumido',)

    list_filter = ('genero', 'ativo', 'criado_em')

    search_fields = ('texto',)

    list_editable = ('ativo',)

    ordering = ('-vezes_respondida', '-criado_em')

    def texto_resumido(self, obj):
        return obj.texto[:50] + ('...' if len(obj.texto) > 50 else '')
    texto_resumido.short_description = 'Pergunta'