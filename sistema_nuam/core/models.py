from django.db import models
import base64

class CalificacionTributaria(models.Model):
    # --- Identificación ---
    rut_cliente = models.CharField(max_length=255, verbose_name="RUT Encriptado")
    razon_social = models.CharField(max_length=255, default="Sin Nombre", verbose_name="Razón Social")
    
    # --- Datos Generales (Excel 3.1) ---
    ejercicio = models.IntegerField(default=2025, verbose_name="Ejercicio")
    mercado = models.CharField(max_length=10, verbose_name="Mercado")
    instrumento = models.CharField(max_length=50, verbose_name="Instrumento")
    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha Pago")
    secuencia = models.BigIntegerField(default=0, verbose_name="Secuencia")
    numero_dividendo = models.BigIntegerField(default=0, verbose_name="N° Dividendo")
    tipo_sociedad = models.CharField(max_length=1, choices=[('A', 'Abierta'), ('C', 'Cerrada')], default='A')
    valor_historico = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    # --- NUEVOS CAMPOS ---
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    # ELIMINADO: es_isfut
    factor_actualizacion = models.DecimalField(max_digits=10, decimal_places=8, default=0.0, verbose_name="Factor Actualización")
    origen = models.CharField(max_length=20, default="MANUAL", verbose_name="Origen de Datos")

    # --- Factores 8 al 37 ---
    factor_8 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_9 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_10 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_11 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_12 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_13 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_14 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_15 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_16 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_17 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_18 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_19 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_20 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_21 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_22 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_23 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_24 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_25 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_26 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_27 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_28 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_29 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_30 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_31 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_32 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_33 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_34 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_35 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_36 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    factor_37 = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            base64.b64decode(self.rut_cliente, validate=True)
        except Exception:
            rut_bytes = self.rut_cliente.encode('utf-8')
            self.rut_cliente = base64.b64encode(rut_bytes).decode('utf-8')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.instrumento} - {self.fecha_creacion}"