from django.shortcuts import render,redirect
from django.forms import inlineformset_factory
from .models import *
from .forms import OrderForm
from .filters import OrderFilter
from .forms import CreateUserForm,CustomerForm
from django.contrib import messages
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_user,admin_only
from django.contrib.auth.models import Group

@login_required
@admin_only
def home(request):
    orders=Order.objects.all()
    customers=Customer.objects.all()
    total_customers=customers.count()
    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    context={
        'orders':orders,
        'customers':customers,
        'total_customers':total_customers,
        'total_orders':total_orders,
        'delivered':delivered,
        'pending':pending
    }
    return render(request,'accounts/dashboard.html',context)

@login_required
@allowed_user(allowed_roles=['admin'])
def products(request):
    products=Product.objects.all()
    return render(request,'accounts/products.html', {'products':products})

@login_required
@allowed_user(allowed_roles=['admin'])
def customers(request,pk_test):
    customer=Customer.objects.get(id=pk_test)
    orders=customer.order_set.all()
    order_count=orders.count()
    my_filter=OrderFilter(request.GET,queryset=orders)
    orders=my_filter.qs
    context={
        'customer':customer,
        'orders':orders,
        'order_count':order_count,
        'filter':my_filter,
    }
    return render(request,'accounts/customer.html',context)

@login_required
@allowed_user(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFormSet=inlineformset_factory(Customer,Order,fields=('product','status'),extra=5)
    customer=Customer.objects.get(id=pk)
    formset=OrderFormSet(queryset=Order.objects.none(),instance=customer)
    if request.method=='POST':
        formset=OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context={
        'form':formset,
    }
    return render(request,'accounts/order_form.html',context)

@login_required
@allowed_user(allowed_roles=['admin'])
def updateOrder(request,pk):
    order=Order.objects.get(id=pk)
    form=OrderForm(instance=order)
    if request.method=='POST':
        form=OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('account-home')
    context = {
        'form': form,
    }
    return render(request, 'accounts/order_form.html', context)

@login_required
@allowed_user(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('account-home')
    context={'item':order}
    return render(request, 'accounts/delete.html', context)

@unauthenticated_user
def registerPage(request):
    form=CreateUserForm()
    if request.method=='POST':
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,"Account Created Successfully for " + username)
            return redirect('login')
    context={'form':form}
    return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('account-home')
        else:
            messages.info(request,'Username or password is incorrect')
    context={}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
@allowed_user(allowed_roles=['customer'])
def userPage(request):
    orders=request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context={'orders':orders,
             'total_orders': total_orders,
             'delivered': delivered,
             'pending': pending
             }
    return render(request,'accounts/user.html',context)

@login_required
@allowed_user(allowed_roles=['customer'])
def accountSettings(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)
    if request.method=='POST':
        form=CustomerForm(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()
            return redirect('account')
    context={'form':form}
    return render(request,'accounts/account_settings.html',context)