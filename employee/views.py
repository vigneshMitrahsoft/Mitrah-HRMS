from django.shortcuts import render,HttpResponse

def testing(request):
    return render(request,"index.html")
