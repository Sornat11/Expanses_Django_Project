from collections import OrderedDict

from django.db.models import Sum, Value, F, Count
from django.db.models.functions import Coalesce

from .models import Category


def summary_per_category(queryset):
    return OrderedDict(sorted(
        queryset
        .annotate(category_name=Coalesce('category__name', Value('-')))
        .order_by()
        .values('category_name')
        .annotate(s=Sum('amount'))
        .values_list('category_name', 's')
    ))

def summary_per_year_month(queryset):
    return (
        queryset
        .annotate(year=F('date__year'), month=F('date__month'))
        .values('year', 'month')
        .annotate(total_amount=Sum('amount'))
        .order_by('-year', '-month')
    )

def total_spent(queryset):
    total = queryset.aggregate(total_amount=Sum('amount'))['total_amount']
    return total or 0

def get_categories_with_expense_count():
    return Category.objects.annotate(expenses_count=Count('expense'))


