from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

import pdb
from .models import *
from . import forms as ac_forms

def index(request):
    context = {}
    template = loader.get_template('ac_seguridad/index.html')
    return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. You're at the polls index.")
    
def ver_pagina(request):
    context = {}
    template = loader.get_template('ac_seguridad/ver_pagina.html')
    return HttpResponse(template.render(context, request))

def contacto(request):
    context = {}
    template = loader.get_template('ac_seguridad/contacto.html')
    return HttpResponse(template.render(context, request))
    
def afiliados(request):
    context = {}
    template = loader.get_template('ac_seguridad/afiliados.html')
    return HttpResponse(template.render(context, request))
    
def registro_persona(request):
    context=dict()
    
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        persona_form = ac_forms.SignUpPersonaForm(request.POST)
        if (user_form.is_valid() and persona_form.is_valid()):
            # Aquí se guarda el usuario creado en AUTH users
            usuario_user = user_form.save() 
            usuario_user.refresh_from_db()
            
            # Extraemos los datos del form de persona.
            cedula_persona = persona_form.cleaned_data.get('cedula')
            email_persona = persona_form.cleaned_data.get('email')
            nombre_persona = persona_form.cleaned_data.get('nombre')
            apellido_persona = persona_form.cleaned_data.get('apellido')
            telefono_persona = persona_form.cleaned_data.get('telefono')
            
            usuario_persona = Persona(
                                usuario=usuario_user, 
                                nombre=nombre_persona,
                                apellido=apellido_persona,
                                telefono=telefono_persona,
                                cedula=cedula_persona,
                                email=email_persona)
            
            usuario_persona.save()
            usuario_user.save()
            
            # Extraer los datos de cada form.
            nombre_usuario = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            
            usuario = authenticate(username=nombre_usuario, password=raw_password)
            # Authenticate regresa un objeto Usuario si logra autenticar, 
            # Retorna None si NO pudo autenticar. En este caso, como estamos 
            # creando el usuario, siempre debería autenticar.
            if usuario is not None:
                login(request, usuario)
                return redirect('area_personal')
            else:
                return redirect('login')
                
    else:
        persona_form = ac_forms.SignUpPersonaForm()
        user_form = UserCreationForm()
        
    context['user_form'] = user_form
    context['persona_form'] = persona_form
    return render(request, 'ac_seguridad/registration/signup_persona.html', context)
    
def registro_estacionamiento(request):
    context=dict()
    
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        estacionamiento_form = ac_forms.SignUpEstacionamientoForm(request.POST)
        if (user_form.is_valid() and estacionamiento_form.is_valid()):
            # Aquí se guarda el usuario creado en AUTH users
            usuario_user = user_form.save() 
            usuario_user.refresh_from_db()
            
            # Extraemos los datos del form de estacionamiento.
            rif_estacionamiento = estacionamiento_form.cleaned_data.get('rif')
            email_estacionamiento = estacionamiento_form.cleaned_data.get('email')
            nombre_estacionamiento = estacionamiento_form.cleaned_data.get('nombre')
            numero_de_puestos_estacionamiento = estacionamiento_form.cleaned_data.get('numero_de_puestos')
            acceso_restringido_estacionamiento = estacionamiento_form.cleaned_data.get('acceso_restringido')
            
            
            usuario_estacionamiento = Estacionamiento(
                                        usuario = usuario_user,
                                        rif = rif_estacionamiento,
                                        nombre = nombre_estacionamiento,
                                        numero_de_puestos = numero_de_puestos_estacionamiento,
                                        acceso_restringido = acceso_restringido_estacionamiento,
                                        email = email_estacionamiento)
            
            usuario_estacionamiento.save()
            usuario_user.save()
            
            # Extraer los datos de cada form.
            nombre_usuario = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            
            usuario = authenticate(username=nombre_usuario, password=raw_password)
            if usuario is not None:
                login(request, usuario)
                return redirect('area_empresas')
            else:
                return redirect('login')
    else:
        estacionamiento_form = ac_forms.SignUpEstacionamientoForm()
        user_form = UserCreationForm()
        
    context['user_form'] = user_form
    context['estacionamiento_form'] = estacionamiento_form
    return render(request, 'ac_seguridad/registration/signup_estacionamiento.html', context)
    
@login_required
def area_personal(request):
    # Esta página sólo es visible para el usuario que ha hecho login. 
    # Django nos garantiza al usar el @login_required que sólo se podrá entrar
    # en esta página si el usuario está logueado. También, en request.user
    # estará la instancia de usuario 'User'.
    context = dict()
    try:
        usuario = request.user.persona
    except:
        return redirect('index')
    
    # Obtener la lista de vehículos que la persona posee. 
    # Aquí tenemos que forzar la evaluación con list() porque necesitaremos
    # las placas para los tickets.
    vehiculos_usuario = list(Vehiculo.objects.filter(dueno=usuario.cedula))
    
    lista_placas = [vehiculo.placa for vehiculo in vehiculos_usuario]
    
    # Obtener la lista de tickets.
    # pdb.set_trace()
    # Al usar placa__in le decimos que la placa tiene que ser alguna de las
    # que esté en la lista.
    # Forzamos a realizar la búsqueda en la BD.
    tickets_usuario = list(Ticket.objects.filter(placa__in=lista_placas))
    
    # Obtener la lista de tickets.
    # pdb.set_trace()
    # Al usar placa__in le decimos que la placa tiene que ser alguna de las
    # que esté en la lista.
    # Forzamos a realizar la búsqueda en la BD.
    avisos_usuario = list(Alerta.objects.filter(usuario=usuario.cedula))
    
    context['vehiculos_usuario'] = vehiculos_usuario
    context['tickets_usuario'] = tickets_usuario
    context['avisos_usuario'] = avisos_usuario
    context['usuario'] = usuario
    template = loader.get_template('ac_seguridad/area_personal/area_personal.html')
        
    return HttpResponse(template.render(context,request))

@login_required
def area_empresas(request):
    # Esta página sólo es visible para el usuario que ha hecho login. 
    # Django nos garantiza al usar el @login_required que sólo se podrá entrar
    # en esta página si el usuario está logueado. También, en request.user
    # estará la instancia de usuario 'User'.
    context = dict()
    try:
        estacionamiento = request.user.estacionamiento
    except:
        return redirect('index')
    
    # # Obtener la lista de vehículos que la persona posee. 
    # # Aquí tenemos que forzar la evaluación con list() porque necesitaremos
    # # las placas para los tickets.
    # vehiculos_usuario = list(Vehiculo.objects.filter(dueno=usuario.cedula))
    
    # lista_placas = [vehiculo.placa for vehiculo in vehiculos_usuario]
    
    # # Obtener la lista de tickets.
    # # pdb.set_trace()
    # # Al usar placa__in le decimos que la placa tiene que ser alguna de las
    # # que esté en la lista.
    # # Forzamos a realizar la búsqueda en la BD.
    # tickets_usuario = list(Ticket.objects.filter(placa__in=lista_placas))
    
    # # Obtener la lista de tickets.
    # # pdb.set_trace()
    # # Al usar placa__in le decimos que la placa tiene que ser alguna de las
    # # que esté en la lista.
    # # Forzamos a realizar la búsqueda en la BD.
    # avisos_usuario = list(Alerta.objects.filter(usuario=usuario.cedula))
    
    # context['vehiculos_usuario'] = vehiculos_usuario
    # context['tickets_usuario'] = tickets_usuario
    # context['avisos_usuario'] = avisos_usuario
    context['estacionamiento'] = estacionamiento
    template = loader.get_template('ac_seguridad/area_empresas/area_empresas.html')
        
    return HttpResponse(template.render(context,request))

@login_required
def registro_vehiculo(request):
    usuario = request.user.persona
    
    context = dict()
    if request.method == 'POST':
        vehiculo_form = ac_forms.VehiculoForm(request.POST)
        if (vehiculo_form.is_valid()):
            
            # Extraemos los datos del form de estacionamiento.
            placa = vehiculo_form.cleaned_data.get('placa')
            marca = vehiculo_form.cleaned_data.get('marca')
            modelo = vehiculo_form.cleaned_data.get('modelo')
            year = vehiculo_form.cleaned_data.get('year')
            
            vehiculo = Vehiculo(
                                dueno = usuario,
                                placa = placa,
                                marca = marca,
                                modelo = modelo,
                                year = year)
            vehiculo.save()
            
            # Redirigir a area personal.
            return redirect('area_personal')
    else:
        vehiculo_form = ac_forms.VehiculoForm()
        
    context['vehiculo_form'] = vehiculo_form
    return render(request, 'ac_seguridad/area_personal/registro_vehiculo.html', context)

@login_required
def pago_estacionamiento(request):
    context=dict()
    
    estacionamiento = request.user.estacionamiento
    es_tarifa_plana = estacionamiento.tarifa_plana
    monto_tarifa = estacionamiento.monto_tarifa
    # pdb.set_trace()
    if request.method == 'POST':
        pago_form = ac_forms.PagoEstacionamientoForm(request.POST)
        if (pago_form.is_valid()):
            
            # Extraemos los datos del form de pago.
            num_ticket = pago_form.cleaned_data.get('numero_ticket')
            registrado_ticket = pago_form.cleaned_data.get('registrado_ticket')
            
            try:
                if (registrado_ticket):
                    ticket = Ticket.objects.get(numero_ticket=num_ticket)
                    placa = ticket.placa.placa
                else:
                    ticket = TicketNoRegistrado.objects.get(numero_ticket=num_ticket)
                    placa = ticket.placa
            except:
                return redirect('pago_estacionamiento')
            
            # Tiempo transcurrido.
            tiempo_transcurrido = timezone.now() - ticket.hora_entrada
            if (es_tarifa_plana):
                monto_a_pagar = monto_tarifa * (1 + tiempo_transcurrido.days)
            else:
                horas = round(tiempo_transcurrido.total_seconds() / 3600)
                monto_a_pagar = monto_tarifa * horas
            
            context['monto_tarifa'] = monto_tarifa
            context['es_tarifa_plana'] = es_tarifa_plana
            context['hora_entrada'] = ticket.hora_entrada
            context['registrado_ticket'] = registrado_ticket
            context['tiempo_transcurrido'] = tiempo_transcurrido
            context['monto_a_pagar'] = monto_a_pagar
            context['num_ticket'] = num_ticket
            context['placa']= placa
            
    else:
        pago_form = ac_forms.PagoEstacionamientoForm()
        
    context['pago_form'] = pago_form
    return render(request, 'ac_seguridad/area_empresas/pago_estacionamiento.html', context)    

@login_required
def pagar_ticket(request):
    context=dict()
    if request.method == 'POST':
        ticket_id = request.POST['numero_ticket']
        registrado = request.POST['registrado_ticket']
        try:
            if (registrado):
                ticket = Ticket.objects.get(numero_ticket=ticket_id)
            else:
                ticket = TicketNoRegistrado.objects.get(numero_ticket=ticket_id)
            ticket.pagado = True
            ticket.save()
        except:
            return redirect('pago_estacionamiento')
        
    return redirect('pago_estacionamiento') 