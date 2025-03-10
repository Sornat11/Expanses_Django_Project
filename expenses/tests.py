import datetime
from django.test import TestCase
from expenses.models import Category, Expense
from .forms import ExpenseSearchForm
from django.urls import reverse


class CategoryModelTest(TestCase):

    def test_string_representation(self):
        category = Category.objects.create(name="Groceries")
        self.assertEqual(str(category), "Groceries")

    def test_category_ordering(self):
        Category.objects.create(name="Zebra")
        Category.objects.create(name="Apple")
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Apple")


class ExpenseModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Transport")

    def test_string_representation(self):
        expense = Expense.objects.create(
            name="Bus ticket",
            amount=3.50,
            category=self.category,
            date=datetime.date(2024, 1, 1)
        )
        expected_str = "2024-01-01 Bus ticket 3.50"
        self.assertEqual(str(expense), expected_str)

    def test_expense_ordering(self):
        expense1 = Expense.objects.create(
            name="Bus ticket",
            amount=3.50,
            category=self.category,
            date=datetime.date(2024, 1, 2)
        )
        expense2 = Expense.objects.create(
            name="Tram ticket",
            amount=4.00,
            category=self.category,
            date=datetime.date(2024, 1, 1)
        )
        expenses = Expense.objects.all()
        # Najnowszy powinien być pierwszy (po dacie malejąco)
        self.assertEqual(expenses[0], expense1)
        self.assertEqual(expenses[1], expense2)

    def test_create_expense_without_category(self):
        expense = Expense.objects.create(
            name="No category expense",
            amount=10.00,
            date=datetime.date.today()
        )
        self.assertIsNone(expense.category)
        self.assertEqual(expense.name, "No category expense")

class ExpenseSearchFormTest(TestCase):

    def setUp(self):
        # Tworzymy jedną kategorię testową
        self.category1 = Category.objects.create(name="Groceries")
        self.category2 = Category.objects.create(name="Transport")

    def test_form_valid_data(self):
        form_data = {
            'name': 'Lunch',
            'date_from': '2024-01-01',
            'date_to': '2024-02-01',
            'category': [self.category1.id, self.category2.id],
            'sort_by': 'date',
            'order': 'asc'
        }
        form = ExpenseSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Lunch')

    def test_form_without_dates(self):
        # Formularz powinien być poprawny nawet bez dat
        form_data = {
            'name': 'Lunch',
            'category': [self.category1.id],
            'sort_by': 'category',
            'order': 'desc'
        }
        form = ExpenseSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_date_range(self):
        # date_from > date_to, formularz nie powinien być poprawny
        form_data = {
            'date_from': '2024-03-01',
            'date_to': '2024-02-01'
        }
        form = ExpenseSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The start date (date_from) cannot be later than the end date (date_to).",
            form.non_field_errors()
        )

    def test_empty_form_is_valid(self):
        # Pusty formularz powinien być poprawny
        form = ExpenseSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_default_sort_and_order(self):
        form_data = {
            'name': 'Coffee'
        }
        form = ExpenseSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Sprawdzamy, czy pola sort_by i order przyjmują wartości domyślne
        self.assertEqual(form.fields['sort_by'].initial, 'date')
        self.assertEqual(form.fields['order'].initial, 'asc')


class ExpenseListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cat_food = Category.objects.create(name='Food')
        cls.cat_travel = Category.objects.create(name='Travel')
        Expense.objects.create(name='Pizza', amount=50, date='2024-01-10', category=cls.cat_food)
        Expense.objects.create(name='Burger', amount=30, date='2024-01-12', category=cls.cat_food)
        Expense.objects.create(name='Flight', amount=300, date='2024-02-01', category=cls.cat_travel)

    def test_expense_list_view_status_code(self):
        response = self.client.get(reverse('expenses:expense-list'))  # Używamy 'expense-list' zamiast 'expenses:list'
        self.assertEqual(response.status_code, 200)

    def test_expense_list_view_context(self):
        response = self.client.get(reverse('expenses:expense-list'))
        self.assertIn('form', response.context)
        self.assertIn('object_list', response.context)
        self.assertIn('total_spent', response.context)
        self.assertIn('summary_per_category', response.context)
        self.assertIn('summary_per_year_month', response.context)

    def test_expense_list_filter_by_name(self):
        response = self.client.get(reverse('expenses:expense-list'), {'name': 'Pizza'})
        expenses = response.context['object_list']
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].name, 'Pizza')

    def test_expense_list_filter_by_date_range(self):
        response = self.client.get(reverse('expenses:expense-list'), {'date_from': '2024-01-01', 'date_to': '2024-01-31'})
        expenses = response.context['object_list']
        self.assertEqual(len(expenses), 2)  # Pizza + Burger

    def test_expense_list_filter_by_category(self):
        response = self.client.get(reverse('expenses:expense-list'), {'category': [self.cat_travel.id]})
        expenses = response.context['object_list']
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].name, 'Flight')

    def test_expense_list_sort_by_date_desc(self):
        response = self.client.get(reverse('expenses:expense-list'), {'sort_by': 'date', 'order': 'desc'})
        expenses = response.context['object_list']
        self.assertEqual(expenses[0].name, 'Flight')  # Najnowszy

    def test_expense_list_sort_by_category_asc(self):
        response = self.client.get(reverse('expenses:expense-list'), {'sort_by': 'category', 'order': 'asc'})
        expenses = response.context['object_list']
        self.assertEqual(expenses[0].category.name, 'Food')


class CategoryListViewTest(TestCase):
    def setUp(self):
    
        food = Category.objects.create(name='Food')
        travel = Category.objects.create(name='Travel')

        Expense.objects.create(name='Lunch', amount=100, category=food)
        Expense.objects.create(name='Trip', amount=500, category=travel)

    def test_category_list_with_expense_count(self):
        response = self.client.get(reverse('expenses:category-list'))
        categories = response.context['object_list']
        self.assertEqual(len(categories), 2)  
        
        food_category = next(cat for cat in categories if cat.name == 'Food')
        travel_category = next(cat for cat in categories if cat.name == 'Travel')

        self.assertEqual(food_category.expenses_count, 1)
        self.assertEqual(travel_category.expenses_count, 1)

