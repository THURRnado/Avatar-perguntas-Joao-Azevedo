from django.db import models


class Pergunta(models.Model):
    texto = models.TextField()

    criado_em = models.DateTimeField(auto_now_add=True)
    modificado_em = models.DateTimeField(auto_now=True)

    GENEROS = [
        ('BIO', 'Biografia'),
        ('OBR', 'Obras'),
        ('ACO', 'Ações do governo'),
    ]
    genero = models.CharField(max_length=3, choices=GENEROS, default='PES')

    vezes_respondida = models.PositiveIntegerField(default=0)

    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-vezes_respondida', '-criado_em']

    def __str__(self):
        return self.texto[:50]