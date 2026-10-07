from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Cliente, EstadoCaso, Caso, Expediente, Pago, PerfilAbogado

class PerfilAbogadoInline(admin.StackedInline):
    model = PerfilAbogado
    can_delete = False
    verbose_name_plural = 'Perfil de Abogado'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilAbogadoInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'documento', 'telefono', 'correo')
    search_fields = ('nombres', 'documento')

@admin.register(EstadoCaso)
class EstadoCasoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'permite_pagos')
    list_filter = ('permite_pagos',)

class ExpedienteInline(admin.TabularInline):
    model = Expediente
    extra = 1

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1

@admin.register(Caso)
class CasoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'cliente', 'estado', 'obtener_total_pagado')
    search_fields = ('codigo', 'titulo', 'cliente__nombres')
    list_filter = ('estado', 'fecha_inicio')
    filter_horizontal = ('abogados',)
    inlines = [ExpedienteInline, PagoInline]

    def obtener_total_pagado(self, obj):
        return f"S/. {obj.total_pagado():.2f}"
    obtener_total_pagado.short_description = 'Total Pagado'

@admin.register(Expediente)
class ExpedienteAdmin(admin.ModelAdmin):
    list_display = ('numero', 'juzgado', 'caso', 'fecha_presentacion')
    search_fields = ('numero', 'juzgado')