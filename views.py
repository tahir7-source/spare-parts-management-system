from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import csv
from django.db.models import Sum
from .models import Sale, Purchase
from decimal import Decimal
from datetime import datetime


def index(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'index.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SparePart, Category

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SparePart

@login_required
def home(request):
    query = request.GET.get('q', '')

    # Search by part name if a query is provided
    if query:
        spare_parts = SparePart.objects.filter(name__icontains=query)
    else:
        spare_parts = SparePart.objects.all()

    return render(request, 'home.html', {
        'spare_parts': spare_parts,
        'query': query,
    })

from .models import SparePart, Purchase, Sale


@login_required
def purchase_or_sale(request):
    if request.method == 'POST':
        spare_part_id = request.POST.get('spare_part')
        quantity = int(request.POST.get('quantity'))
        action = request.POST.get('action')

        spare_part = SparePart.objects.get(id=spare_part_id)

        # Define pricing strategy
        purchase_price = (spare_part.price) 
        sale_price = Decimal(spare_part.price) * Decimal('1.2')  # 20% higher

        if action == 'purchase':
            # Handle purchase with the correct price
            Purchase.objects.create(spare_part=spare_part, quantity=quantity, purchase_price=purchase_price)
            messages.success(request, f'Successfully purchased {quantity} units of {spare_part.name} at {purchase_price}.')
        elif action == 'sale':
            # Handle sale with the correct price
            if quantity <= spare_part.quantity_in_stock:
                Sale.objects.create(spare_part=spare_part, quantity=quantity, sale_price=sale_price)
                messages.success(request, f'Successfully sold {quantity} units of {spare_part.name} at {sale_price}.')
            else:
                messages.error(request, f'Not enough stock for {spare_part.name}.')
       
    return redirect('home')


def logout_view(request):
    logout(request)
    return redirect('index')  



def report_view(request):
    # Initialize empty lists for reports and profit
    sales = []
    purchases = []
    profit = 0

    # Default date range (last 30 days)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            start_date = None
            end_date = None

    # Query based on date range
    if start_date and end_date:
        sales = Sale.objects.filter(date__range=[start_date, end_date])
        purchases = Purchase.objects.filter(date__range=[start_date, end_date])
    else:
        sales = Sale.objects.all()
        purchases = Purchase.objects.all()

    # Calculate total sales and purchases
    total_sales = sales.aggregate(total=Sum('total_price'))['total'] or 0
    total_purchases = purchases.aggregate(total=Sum('total_price'))['total'] or 0
    profit = total_sales - total_purchases

    # If no records found, show a message
    no_records_message = "No records found for the selected date range." if not sales and not purchases else ""

    context = {
        'sales': sales,
        'purchases': purchases,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'profit': profit,
        'no_records_message': no_records_message,
    }

    return render(request, 'report.html', context)




def download_csv(request):
    start_date = request.POST.get('start_date', None)
    end_date = request.POST.get('end_date', None)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Item', 'Quantity', 'Price', 'Total Price', 'Date'])

    if start_date and end_date:
        from datetime import datetime
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            start_date = None
            end_date = None

    if start_date and end_date:
        sales = Sale.objects.filter(date__range=[start_date, end_date])
        purchases = Purchase.objects.filter(date__range=[start_date, end_date])
    else:
        sales = Sale.objects.all()
        purchases = Purchase.objects.all()

    # Write sales to CSV
    for sale in sales:
        writer.writerow(['Sale', sale.spare_part.name, sale.quantity, sale.sale_price, sale.total_price, sale.date])

    # Write purchases to CSV
    for purchase in purchases:
        writer.writerow(['Purchase', purchase.spare_part.name, purchase.quantity, purchase.purchase_price, purchase.total_price, purchase.date])

    return response

from django.shortcuts import render, redirect, get_object_or_404
from .models import SparePart

def update_spare_part(request, id):
    part = get_object_or_404(SparePart, id=id)  # Ensure the part is correctly fetched
    if request.method == 'POST':
        part.name = request.POST.get('name')
        part.price = request.POST.get('price')
        part.quantity_in_stock = request.POST.get('quantity_in_stock')
        part.save()  # Save the updated part
        return redirect('home')  # Redirect back to the home page
    return render(request, 'update_spare_part.html', {'part': part})

def delete_spare_part(request, id):
    part = get_object_or_404(SparePart, id=id)
    part.delete()
    return redirect('home')
