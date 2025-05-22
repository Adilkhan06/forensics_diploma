from django.db import models

from ingest.models import File

class AnalysisSession(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Сессия от {self.started_at.strftime('%d.%m.%Y %H:%M')}"

class Match(models.Model):
    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        null=False,
        blank=True
    )
    source_file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='source_matches')
    target_file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='target_matches')

    similarity_score = models.FloatField()
    match_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    matched_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Совпадение {self.source_file} - {self.target_file}: {self.similarity_score:.2f}"


