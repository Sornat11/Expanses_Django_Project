from django.views.generic.list import ListView

from .forms import ExpenseSearchForm
from .models import Expense, Category
from .reports import summary_per_category
from django.db.models import F, Sum, Count

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

            if name:
                queryset = queryset.filter(name__icontains=name)
        
            if date_from:
                queryset = queryset.filter(date__gte=date_from)

            if date_to:
                queryset = queryset.filter(date__lte=date_to)

            if categories:
                queryset = queryset.filter(category__in=categories)
        
        
        sort_by = self.request.GET.get('sort_by', 'date')  
        order = self.request.GET.get('order', 'asc')  

        if sort_by == 'category':
            queryset = queryset.order_by(F('category').desc() if order == 'desc' else F('category').asc())
        elif sort_by == 'date':
            queryset = queryset.order_by(F('date').desc() if order == 'desc' else F('date').asc())

        total_spent = queryset.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        year_month_summary = (
            queryset
            .annotate(year=F('date__year'), month=F('date__month'))
            .values('year', 'month')
            .annotate(total_amount=Sum('amount'))
            .order_by('-year', '-month')
        )

        return super().get_context_data(
            form=form,
            object_list=queryset,
            summary_per_category=summary_per_category(queryset),
            total_spent=total_spent,
            summary_per_year_month=year_month_summary,
            **kwargs)

class CategoryListView(ListView):
    model = Category
    paginate_by = 5

    def get_queryset(self):
        return Category.objects.annotate(expenses_count=Count('expense'))