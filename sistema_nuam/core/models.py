from django.db import models
import base64

class CalificacionTributaria(models.Model):
    # Campos existentes
    rut_cliente = models.CharField(max_length=255, verbose_name="RUT Encriptado")
    
    # --- CAMPOS NUEVOS (LO QUE FALTABA) ---
    razon_social = models.CharField(max_length=255, default="Sin Nombre", verbose_name="Razón Social")
    anio = models.IntegerField(default=2025, verbose_name="Año Tributario")
    # --------------------------------------

    factor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Lógica de encriptación (se mantiene igual)
        try:
            base64.b64decode(self.rut_cliente, validate=True)
        except Exception:
            rut_bytes = self.rut_cliente.encode('utf-8')
            self.rut_cliente = base64.b64encode(rut_bytes).decode('utf-8')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.razon_social} ({self.anio})"