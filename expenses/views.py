from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category, summary_per_year_month, total_spent, get_categories_with_expense_count
from django.db.models import F

class ExpenseListView(ListView):
    model = Expense
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list

        form = ExpenseSearchForm(self.request.GET)
        if form.is_valid():
            name = form.cleaned_data.get('name', '').strip()
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            categories = form.cleaned_data.get('category')
            sort_by = form.cleaned_data.get('sort_by') or 'date'  # Domyślna wartość
            order = form.cleaned_data.get('order') or 'asc'

            if name:
                queryset = queryset.filter(name__icontains=name)
        
            if date_from:
                queryset = queryset.filter(date__gte=date_from)

            if date_to:
                queryset = queryset.filter(date__lte=date_to)

            if categories:
                queryset = queryset.filter(category__in=categories)
        


        if sort_by == 'category':
            queryset = queryset.order_by(F('category').desc() if order == 'desc' else F('category').asc())
        elif sort_by == 'date':
            queryset = queryset.order_by(F('date').desc() if order == 'desc' else F('date').asc())

        total = total_spent(queryset)
        category_summary = summary_per_category(queryset)
        year_month_summary = summary_per_year_month(queryset)

        return super().get_context_data(
            form=form,
            object_list=queryset,
            total_spent=total,
            summary_per_category=category_summary,
            summary_per_year_month=year_month_summary,
            sort_by=sort_by,  
            order=order,
            **kwargs
        )


class CategoryListView(ListView):
    model = Category

    def get_queryset(self):
        return get_categories_with_expense_count()