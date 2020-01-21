from django.shortcuts import render,HttpResponse,redirect
from .models import Product, Contact, Orders, OrderUpdate
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
# from PayTm import Checksum
# # Create your views here.
from django.http import HttpResponse
# MERCHANT_KEY = 'my merchnt key Here'

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')


def handleLogin(request):
    if request .method == 'POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']
        user = authenticate(username=loginusername, password=loginpassword)

        if user is not None:
            login(request,user)
            messages.success(request," Successfully Logged In")
            return redirect('/')

        else:
            print("successfully login bro")
            messages.error(request,"invalid credentials, Plese Try Again:")
            return redirect('home')

    return HttpResponse('404 is page not found For Login page')     



    
def handleLogout(request):
    logout(request)
    messages.success(request," Successfully Logged Out")
    return redirect('/')




def handleSignup(request):
    if request.method == 'POST':
        # get the post parameters
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # check for errorneouus inputs

        if len(username) > 10:
            messages.error(request,"username must be under 10 chracters")
            return redirect('/')

        
        if not username.isalnum():
            messages.error(request,"username should only contain letters and numbers")
            return redirect('/')
        

        if pass1 != pass2:
            messages.error(request," Password Do Not Matched")
            return redirect('/')


        # create the user 
        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request,'your Account is SptechGuru has been successfully createed')
        return redirect('/')

    else:
        return HttpResponse('404 is page not found')




def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
        params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')



def contact(request):
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
    return render(request, 'shop/contact.html')
    


 # Paytm gateway

# def tracker(request):
#     if request.method=="POST":
#         orderId = request.POST.get('orderId', '')
#         email = request.POST.get('email', '')
#         try:
#             order = Orders.objects.filter(order_id=orderId, email=email)
#             if len(order)>0:
#                 update = OrderUpdate.objects.filter(order_id=orderId)
#                 updates = []
#                 for item in update:
#                     updates.append({'text': item.update_desc, 'time': item.timestamp})
#                     response = json.dumps([updates, order[0].items_json], default=str)
#                 return HttpResponse(response)
#             else:
#                 return HttpResponse('{"status":"noitem"}')
#         except Exception as e:
#             return HttpResponse('{"status":"error"}')

#     return render(request, 'shop/tracker.html')


# def tracker(request):
#     if request.method=="POST":
#         orderId = request.POST.get('orderId', '')
#         email = request.POST.get('email', '')
#         try:
#             order = Orders.objects.filter(order_id=orderId, email=email)
#             if len(order)>0:
#                 update = OrderUpdate.objects.filter(order_id=orderId)
#                 updates = []
#                 for item in update:
#                     updates.append({'text': item.update_desc, 'time': item.timestamp})
#                     response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
#                 return HttpResponse(response)
#             else:
#                 return HttpResponse('{"status":"noitem"}')
#         except Exception as e:
#             return HttpResponse('{"status":"error"}')
#     return render(request, 'shop/tracker.html')




def prodView(request, myid):
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})



def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Prodcut is Not Found "}
    return render(request, 'shop/search.html', params)


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shop/checkout.html')










    # paytm integrate function 

# def checkout(request):
#     if request.method=="POST":
#         items_json = request.POST.get('itemsJson', '')
#         name = request.POST.get('name', '')
#         amount = request.POST.get('amount', '')
#         email = request.POST.get('email', '')
#         address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         zip_code = request.POST.get('zip_code', '')
#         phone = request.POST.get('phone', '')
#         order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
#                        state=state, zip_code=zip_code, phone=phone, amount=amount)
#         order.save()
#         update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
#         update.save()
#         thank = True
#         id = order.order_id
#         param_dict = {

#                 'MID': 'my merchant Id',
#                 'ORDER_ID': str(order.order_id),
#                 'TXN_AMOUNT': str(amount),
#                 'CUST_ID': email,
#                 'INDUSTRY_TYPE_ID': 'Retail',
#                 'WEBSITE': 'WEBSTAGING',
#                 'CHANNEL_ID': 'WEB',
#                 'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
#         }
#         param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
#         return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
#         # return render(request, 'shop/paytm.html', {'param_dict': param_dict})
#     return render(request, 'shop/checkout.html')



    # paytm integrate function 


# @csrf_exempt
# def handlerequest(request):
#     # paytm will send you post request here
#     form = request.POST
#     response_dict = {}
#     for i in form.keys():
#         response_dict[i] = form[i]
#         if i == 'CHECKSUMHASH':
#             checksum = form[i]
#     verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
#     if verify:
#         if response_dict['RESPCODE'] == '01':
#             print('order successful')
#         else:
#             print('order was not successful because' + response_dict['RESPMSG'])
#     return render(request, 'shop/paymentstatus.html', {'response': response_dict})


