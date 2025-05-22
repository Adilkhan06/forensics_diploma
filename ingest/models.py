import os

from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=255)
    dump_path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class File(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    file_path = models.TextField()
    file_type = models.CharField(max_length=50)
    mime_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    date_created = models.DateTimeField(null=True, blank=True)
    extracted_text = models.TextField(blank=True, null=True)
    embedding = models.BinaryField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    relative_path = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.relative_path or os.path.basename(self.file_path) or f"Файл {self.id}"