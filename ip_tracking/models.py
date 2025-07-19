from django.db import models

# Create your models here.
class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.ip_address} at {self.timestamp} -> {self.path}"
    
    class Meta:
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        ordering = ['-timestamp']  # Order by timestamp descending