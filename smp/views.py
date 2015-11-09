from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from smp.models import Paper,Auther,Jounery
from django.template import Context
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import datetime
import json
import time
#change C4 here
class AF(forms.Form):
		auther =  forms.CharField()
		institution = forms.CharField()
class PF(forms.Form):
		auther =  forms.CharField()
		jounery = forms.CharField()
		institution = forms.CharField()
		pdf = forms.FileField()

class userform(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget = forms.PasswordInput())
def ok():
	return render_to_response("ok.html")
def notvalid():
	return render_to_response("notvalid.html")
# Create your views here.
def getDoc(request):
	   if(request.method == "POST" and request.user is not None):
	      post = request.POST
	      usert = request.user
	      pf = PF(request.POST,request.FILES)
	      if pf.is_valid():
	      	print pf.cleaned_data["pdf"].name
	        a = Auther(
	            name = pf.cleaned_data["auther"],
	            institution=pf.cleaned_data["institution"]    
	        )
	        j = Jounery(
	            J_name=pf.cleaned_data["jounery"]        
	        )
	        p = Paper(
	            user = usert,
	            timestamp = time.localtime(time.time()),
	            pdf = pf.cleaned_data["pdf"],
	            pdfname = pf.cleaned_data["pdf"].name
	            )
	        try:
	        	a = Auther.objects.get(name = a.name)
	        except ObjectDoesNotExist:
	        	a.save()
	        try:
	        	j = Jounery.objects.get(J_name = j.J_name)
	        except ObjectDoesNotExist:
	        	j.save()
	        p.jounery = j
	        p.save()
	        p.MauthorID = a.id
	        p.auther.add(a)
	        p.save()
	        
	        return ok()
	      else:
	        print pf
	        return notvalid()
	   else:
	     return render(request,"upload.html")

def ViewPaper(request):
	dic = {}
	dic['state'] = "0"
	if (request.GET.get('username',False)):
		Get = request.GET
		try:
			usert = User.objects.get(username = Get["username"])
			p = Paper.objects.filter(user = usert)
			if(request.user.is_authenticated()):
				print request.user
				dic['state'] = "1"
			else:
				dic['state'] = '0'
			return render_to_response("view.html",{"paper_list":p,"dic":json.dumps(dic)})
		except ObjectDoesNotExist:
			return notvalid()
	else:
		p = Paper.objects.all()
		return render_to_response("view.html",{"paper_list":p,"dic":json.dumps(dic)})


def register(req):
	if(req.method == "POST"):
		uf = userform(req.POST)
		if uf.is_valid():
			user = User.objects.create_user(
				username = uf.cleaned_data["username"],
				password = uf.cleaned_data["password"]
			)
			user.is_staff = True
			user.save()
			return ok()
		else:
			return notvalid()
	else:
		return render(req,"register.html")

def login_view(request):
	if(request.method == "POST"):
		uf = userform(request.POST)
		if(uf.is_valid()):
			print uf.cleaned_data['username'] 
			print uf.cleaned_data['password']
			user = authenticate(username=request.POST['username'], password=request.POST['password'])
		
			if user:
				login(request, user)
				#response.set_cookie("is_login","1")
				print request.user
				List ={}
				List['state'] = "True"
				List["message"] = "OK!"
				List['name'] = user.username
				response = render(request, 'login.html', {'List': json.dumps(List)})
				response.set_cookie('is_log',1,3600)
				response.set_cookie('username',user.username,3600)
				return response
			else:
				print 1
				List ={}
				List['state'] = "False"
				List["message"] = "password wrong!"
				List['name'] = ""
				return render(request, 'login.html', {'List':json.dumps(List)})
		else:
			print 2
			return notvalid()
	else:
		return render(request,"login.html")

def logout_view(request):
    logout(request)
    response = ok()
    response.delete_cookie('is_log')
    response.delete_cookie('username')
    return response

search_choice = ( 
    ('', u"---------"), 
    (1, u"pdfname"),         
    (2, u"author"),         
    (3, u"jounery"), 
    (4, u"institution"), 
) 

class searchform(forms.Form):
	text = forms.CharField(label = u"search",required = True)
	choice = forms.ChoiceField(label= (u"you choice"),required=True, choices=search_choice)


def Search(request):
	dic = {1:"pdfname",2:"auther",3:"jounery",4:"institution"}
	if(request.method == "POST"):
		back_list = {}
		post = request.POST
		sf = searchform(post)
		if(sf.is_valid()):
			cho = sf.cleaned_data['choice']
			print sf.cleaned_data['choice']
			print cho == 1
			if(cho == '1'):
				#print cho
				back_list = Paper.objects.filter(pdfname = sf.cleaned_data['text'])
			if(cho =='2'):
				au = Auther.objects.get(name = sf.cleaned_data['text'])
				if(not au):
					return notvalid()
				back_list = Paper.objects.filter(auther = au)
			if(cho =='3'):
				jo = Jounery.objects.get(J_name = sf.cleaned_data['text'])
				if(not jo):
					return notvalid()
				back_list = Paper.objects.filter(jounery = jo)
			if(cho =='4'):
				au = Auther.objects.filter(institution = sf.cleaned_data['text'])
				if(not au):
					return notvalid()
				for i in au:
					if(not back_list):
						back_list = Paper.objects.filter(auther = au)
					back_list = back_list | Paper.objects.filter(auther = au)
			return render_to_response("view.html",{"paper_list":back_list})
		else:
			notvalid()
	else:
		return render(request,"search.html")

def showp(req):
	if(req.method == "GET" and req.GET.get('id',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['id'])
		print pap.pdfname
		return render_to_response("detail.html",{"paper":pap})
	return notvalid()


def dele(req):
	if(req.method == "GET" and req.GET.get('id',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['id'])
		if(pap and pap.user ==req.user):
			pap.delete()
			return ok()
		return notvalid()
	return notvalid()

def change(req):
	if(req.method == "GET" and req.GET.get('id',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['id'])
		if(pap and pap.user == req.user):
			au = Auther.objects.get(id = pap.MauthorID)
			#pap.delete()
			return render_to_response("change.html",{"paper":pap,"au":au})
	elif(req.method == "POST" and req.GET.get('id',False)):
		g = req.GET
		pf =PF(req.POST,req.FILES)
		try:
			pap = Paper.objects.get(id = g['id'])
			au = Auther.objects.get(id = pap.MauthorID)
		except ObjectDoesNotExist:
			return notvalid()
		pap.auther.remove(au)
		if(pf.is_valid()):
			a = Auther(
			    name = pf.cleaned_data["auther"],
			    institution=pf.cleaned_data["institution"]    
			)
			j = Jounery(
			    J_name=pf.cleaned_data["jounery"]        
			)
			try:
				a = Auther.objects.get(name = a.name)
			except ObjectDoesNotExist:
				a.save()
			try:
				j = Jounery.objects.get(J_name = j.J_name)
			except ObjectDoesNotExist:
				j.save()
			pap.jounery = j
			pap.pdf = pf.cleaned_data["pdf"]
			pap.pdfname = pf.cleaned_data["pdf"].name
			pap.MauthorID = a.id
			pap.auther.add(a)
			pap.save()
			return ok()
		else:
			return notvalid()
	else:
		return notvalid()



def addauthor(req):
	if(req.method == "GET" and req.GET.get('id',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['id'])
		if(pap and pap.user == req.user):
			af = AF()
			return render(req,"addauthor.html")
	elif(req.method == "POST"):
		g = req.GET
		pap = Paper.objects.get(id = g['id'])
		af = AF(req.POST)
		if(af.is_valid()):
			a = Auther(
	        name = af.cleaned_data["auther"],
	        institution=af.cleaned_data["institution"]
		        )
			try:
				a = Auther.objects.get(name = a.name)
			except ObjectDoesNotExist:
				a.save()
			pap.auther.add(a)
			pap.save()
			return ok()
	else:
		return notvalid()


def changeau(req):
	if(req.method =="POST" and req.GET.get('Aid',False)and req.GET.get('Pid',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['Pid'])
		au = Auther.objects.get(id = g['Aid'])
		aid = au.id
		pap.auther.remove(au)
		af = AF(req.POST)
		if(af.is_valid()):
			a = Auther(
	            name = af.cleaned_data["auther"],
	            institution=af.cleaned_data["institution"]    
	        )
			try:
				a = Auther.objects.get(name = a.name)
			except ObjectDoesNotExist:
				a.save()
			pap.auther.add(a)
			if(pap.MauthorID == aid):
				pap.MauthorID = a.id
			pap.save()
			return ok()
		else:
			return notvalid()
	elif(req.method == "GET" and req.GET.get('Aid',False)and req.GET.get('Pid',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['Pid'])
		au = Auther.objects.get(id = g['Aid'])
		return render_to_response("changeauthor.html",{"au":au})
		return notvalid()
	return notvalid()


def delau(req):
	if(req.method == "GET" and req.GET.get('Aid',False)and req.GET.get('Pid',False)):
		g = req.GET
		pap = Paper.objects.get(id = g['Pid'])
		au = Auther.objects.get(id = g['Aid'])
		if(not (pap.MauthorID == au.id) and pap and pap.user ==req.user):
			pap.auther.remove(au)
			pap.save()
			return ok()
		return notvalid()
	return notvalid()


def sta(req):
	j = Jounery.objects.all()
	for i in j:
		i.jcount = i.paper_set.count()
		if(i.jcount == 0):
			i.delete()
		else:
			i.save()
	a = Auther.objects.all()
	for i in a:
		i.acount = i.paper_set.count()
		print i.paper_set.count()
		if(i.acount == 0):
			i.delete()
		else:
			i.save()
	pnum = Paper.objects.all().count()
	js = Jounery.objects.order_by("jcount")[:5]
	categories =[str(b.J_name) for b in js]
	data = [int(b.jcount) for b in js]
	
	print data
	print categories
	return render_to_response("static.html",{"jnum":j.count(),"anum":a.count(),"pnum":pnum,'user':'hehe','categories':categories,'data':data})
def index(request):
    return render(request,'home.html')

def contact(request):
    return render(request,'contact2.html')

def about(request):
    return render(request,'about2.html')

def show(request):
    return render(request,'show.html')

# def forgotPassword(request):
#     return render(request,'forgot-pass.html')
def getview(request):
    return render(request,'view.html')


def tr(req):
	return render(req,"detail.html")