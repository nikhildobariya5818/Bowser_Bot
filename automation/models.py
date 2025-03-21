from django.db import models

class AutomationLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.timestamp} - {self.ip_address} - {self.status}"
