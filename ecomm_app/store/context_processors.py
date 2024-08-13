from .models import Category

def category_context_processor(request):
    categories = Category.objects.filter(parent__isnull=True)
    return {'categories': categories}
