from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum

class Cliente(models.Model):
    nombres = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    def __str__(self):
        return f"{self.nombres} ({self.documento})"

class EstadoCaso(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    permite_pagos = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class PerfilAbogado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    colegiatura = models.CharField(max_length=50)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.especialidad}"

class Caso(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='casos')
    estado = models.ForeignKey(EstadoCaso, on_delete=models.PROTECT, related_name='casos')
    abogados = models.ManyToManyField(PerfilAbogado, related_name='casos')

    def total_pagado(self):
        total = self.pagos.aggregate(total=Sum('monto'))['total']
        return round(float(total or 0.0), 2)

    def __str__(self):
        return f"{self.codigo} - {self.titulo}"

class Expediente(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    juzgado = models.CharField(max_length=150)
    fecha_presentacion = models.DateField()
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='expedientes')
    documento = models.FileField(upload_to='expedientes/', blank=True, null=True)

    def __str__(self):
        return f"Exp. {self.numero} - {self.juzgado}"

class Pago(models.Model):
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=200)

    def clean(self):
        if self.caso_id and not self.caso.estado.permite_pagos:
            raise ValidationError(f"No se pueden registrar pagos en un caso con estado '{self.caso.estado.nombre}'.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago S/. {self.monto:.2f} - {self.caso.codigo}"