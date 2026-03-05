from django.shortcuts import render, get_object_or_404
from records.search.record_search import birth_search, death_search
from records.models import Person, Birth, Death

def search_birth_records(request):
    if request.htmx:
        filters = {}
        for key, val in request.GET.items():
            if val.strip():
                filters[key] = val.strip()

        if 'birth_year' in filters:
            filters['birth_date'] = filters.pop('birth_year')

        res = birth_search(filters)

        return render(request, 'birth_results.html', {'results': res})
    else:
        return render(request, 'search_birth.html')
    
def search_death_records(request):
    if request.htmx:
        filters = {}
        for key, val in request.GET.items():
            if val.strip():
                filters[key] = val.strip()

        if 'death_year' in filters:
            filters['death_date'] = filters.pop('death_year')

        res = death_search(filters)

        return render(request, 'death_results.html', {'results': res})
    else:
        return render(request, 'search_death.html')

def search_marriage_records(request):
    if request.htmx:
        context = {'results': []}
        return render(request, 'marriage_results.html', context)
    else:
        return render(request, 'search_marriage.html')

def record_details(request, person_id):
    person = get_object_or_404(Person, id = person_id)
    birth = Birth.objects.filter(person = person).first()
    death = Death.objects.filter(person = person).first()

    context = {'person': person,
               'birth': birth,
               'death': death}

    return render(request, 'record_details.html', context)

def home_page(request):
    return render(request, "home_page.html")