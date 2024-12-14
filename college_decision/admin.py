from django.contrib import admin
from .models import Payment, LetterGeneration, UniversityDecision

@admin.register(LetterGeneration)
class LetterGenerationAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'letters_generated', 'first_generated_at', 'last_generated_at')
    search_fields = ('email', 'full_name')
    readonly_fields = ('first_generated_at', 'last_generated_at')
    ordering = ('-last_generated_at',)

@admin.register(UniversityDecision)
class UniversityDecisionAdmin(admin.ModelAdmin):
    list_display = ('university', 'decision_type', 'decision_count')
    list_filter = ('university', 'decision_type')
    ordering = ('university', 'decision_type')

admin.site.register(Payment)
