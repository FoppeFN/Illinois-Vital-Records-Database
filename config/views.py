from django.shortcuts import render

def search_birth_records(request):
    if request.htmx:
        context = {'results': []}
        return render(request, 'birth_results.html', context)
    else:
        return render(request, 'search_birth.html')
    
def search_death_records(request):
    if request.htmx:
        context = {'results': []}
        return render(request, 'death_results.html', context)
    else:
        return render(request, 'search_death.html')

def search_marriage_records(request):
    if request.htmx:
        context = {'results': []}
        return render(request, 'marriage_results.html', context)
    else:
        return render(request, 'search_marriage.html')