from django.shortcuts import render

def search_birth_records(request):
    if request.htmx:
        context = {'results': []}
        return render(request, 'partials/search_results.html', context)
    else:
        return render(request, 'search_birth.html')
    
def search_death_records(request):
    if request.htmx:
        context = {'results': []}
        return render(request, 'partials/search_results.html', context)
    else:
        return render(request, 'search_death.html')