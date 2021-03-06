import requests
import datetime
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm

import environ

def index(request):
    env = environ.Env()
    environ.Env.read_env()

    apikey = env("WEATHER_API")
    units = 'metric'
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid={}'
    url_air = 'https://api.openaq.org/v1/latest'

    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)

        if form.is_valid():
            new_city = form.cleaned_data['name']
            if new_city == '':
                err_msg = 'City name is blank!'
            if City.objects.filter(name=new_city).count() == 0:
                r = requests.get(url.format(new_city, units, apikey)).json()
                if r['cod'] == 200:
                    form.save()
                else:
                    err_msg = 'City does not exist in the world!'
            else:
                err_msg = 'City already exists in the database!'

        if err_msg:
            message = err_msg
            message_class = 'is-danger'
        else:
            message = 'City added successfully!'

    form = CityForm()

    cities = City.objects.all()
    weather_data = []

    for city in cities:
        r = requests.get(url.format(city, units, apikey)).json()

        try:
            air = requests.get(url_air).json()[city.name]
        except:
            air = "N/A"

        print(r)
        city_weather = {
            'city': city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
            'country' : r['sys']['country'],
            'time' : datetime.datetime.now() + datetime.timedelta(seconds = r['timezone']) - datetime.timedelta(seconds = 7200),
            'air' : air,
        }
        weather_data.append(city_weather)

    context = {
        'weather_data' : weather_data,
        'form' : form,
        'message' : message,
        'message_class' : message_class,
        'units' : units,
        }
    print(weather_data)

    return render(request, 'weather/weather.html', context)


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')
