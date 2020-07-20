import requests
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm

def index(request):
    apikey = env("WEATHER_API")
    units = 'metric'
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units={}&appid={}'

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

        city_weather = {
            'city': city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        weather_data.append(city_weather)

    context = {
        'weather_data' : weather_data,
        'form' : form,
        'message' : message,
        'message_class' : message_class,
        }
    print(weather_data)

    return render(request, 'weather/weather.html', context)


def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')
