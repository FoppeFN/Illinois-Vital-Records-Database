import csv
import io

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from records.comment_utils import add_comment
from records.models import Birth, County, Death, Person
from records.search.record_search import birth_search, death_search, marriage_search


def search_birth_records(request):
    if request.htmx:
        filters = {}

        for key, val in request.GET.items():
            if val.strip():
                filters[key] = val.strip()

        if "birth_year" in filters:
            filters["birth_date"] = filters.pop("birth_year")

        if filters.get("variance") == "exact":
            filters["variance"] = 0

        is_fuzzy = bool(filters.pop("fuzzy_search", False))
        res = birth_search(filters, fuzzy=is_fuzzy)
        paginator = Paginator(res, 25)
        page_num = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_num)
        query_dict = request.GET.copy()

        if "page" in query_dict:
            del query_dict["page"]

        curr_query_str = query_dict.urlencode()

        return render(
            request,
            "birth_results.html",
            {"page_obj": page_obj, "curr_query_str": curr_query_str},
        )
    else:
        counties = County.objects.all().order_by("county_name")
        return render(request, "search_birth.html", {"counties": counties})


def search_death_records(request):
    if request.htmx:
        filters = {}

        for key, val in request.GET.items():
            if val.strip():
                filters[key] = val.strip()

        if "death_year" in filters:
            filters["death_date"] = filters.pop("death_year")

        if filters.get("variance") == "exact":
            filters["variance"] = 0

        is_fuzzy = bool(filters.pop("fuzzy_search", False))
        res = death_search(filters, fuzzy=is_fuzzy)
        paginator = Paginator(res, 25)
        page_num = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_num)
        query_dict = request.GET.copy()

        if "page" in query_dict:
            del query_dict["page"]

        curr_query_str = query_dict.urlencode()

        return render(
            request,
            "death_results.html",
            {"page_obj": page_obj, "curr_query_str": curr_query_str},
        )
    else:
        counties = County.objects.all().order_by("county_name")
        return render(request, "search_death.html", {"counties": counties})


def search_marriage_records(request):
    if request.htmx:
        filters = {}

        for key, val in request.GET.items():
            if val.strip():
                filters[key] = val.strip()

        if "marriage_year" in filters:
            filters["marriage_date"] = filters.pop("marriage_year")

        if filters.get("variance") == "exact":
            filters["variance"] = 0

        is_fuzzy = bool(filters.pop("fuzzy_search", False))
        res = marriage_search(filters, fuzzy=is_fuzzy)
        paginator = Paginator(res, 25)
        page_num = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_num)
        query_dict = request.GET.copy()

        if "page" in query_dict:
            del query_dict["page"]

        curr_query_str = query_dict.urlencode()

        return render(
            request,
            "marriage_results.html",
            {"page_obj": page_obj, "curr_query_str": curr_query_str},
        )
    else:
        counties = County.objects.all().order_by("county_name")
        return render(request, "search_marriage.html", {"counties": counties})


def record_details(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    birth = Birth.objects.filter(person=person).first()
    death = Death.objects.filter(person=person).first()

    context = {"person": person, "birth": birth, "death": death}

    return render(request, "record_details.html", context)


def submit_comment(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    fields = {
        "comment_content": request.POST.get("comment_text"),
        "commenter_name": request.POST.get("commenter_name"),
        "commenter_email": request.POST.get("commenter_email"),
    }
    add_comment(person, fields)

    success_message = """
    <div class="text-center p-6 bg-green-50 rounded border border-green-200">
        <h3 class="text-xl font-bold text-forest-green mb-2">Thank you!</h3>
        <p class="text-gray-700">Your information has been successfully submitted to the archive for review.</p>
    </div>
    """
    return HttpResponse(success_message)


def export_csv(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    birth = Birth.objects.filter(person=person).first()
    death = Death.objects.filter(person=person).first()
    # marriages = Marriage.objects.filter(Q(spouse1=person) | Q(spouse2=person))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="{person.last_name}_{person.first_name}_record.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Field", "Value"])
    writer.writerow(["First Name", person.first_name])
    writer.writerow(["Middle Name", person.middle_name or ""])
    writer.writerow(["Last Name", person.last_name])
    writer.writerow(["Sex", person.get_sex_display() or "Unknown"])

    if birth:
        writer.writerow(["Birth Date", birth.birth_date or "N/A"])
        writer.writerow(["Birth City", birth.birth_city or "N/A"])
        writer.writerow(["Birth County", birth.birth_county or "N/A"])

    if death:
        writer.writerow(["Death Date", death.death_date or "N/A"])
        writer.writerow(
            ["Death Age", death.death_age if death.death_age is not None else "N/A"]
        )
        writer.writerow(["Death City", death.death_city or "N/A"])
        writer.writerow(["Death County", death.death_county or "N/A"])

    writer.writerow(
        [
            "Mother",
            f"{person.mother.first_name} {person.mother.last_name}"
            if person.mother
            else "N/A",
        ]
    )
    writer.writerow(
        [
            "Father",
            f"{person.father.first_name} {person.father.last_name}"
            if person.father
            else "N/A",
        ]
    )

    spouses = person.spouses()
    writer.writerow(
        [
            "Spouses",
            ", ".join(f"{s.first_name} {s.last_name}" for s in spouses)
            if spouses
            else "N/A",
        ]
    )

    children = person.children()
    writer.writerow(
        [
            "Children",
            ", ".join(f"{c.first_name} {c.last_name}" for c in children)
            if children
            else "N/A",
        ]
    )

    children = person.children()
    writer.writerow(
        [
            "Children",
            ", ".join(f"{c.first_name} {c.last_name}" for c in children)
            if children
            else "N/A",
        ]
    )

    return response


def export_pdf(request, person_id):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    person = get_object_or_404(Person, id=person_id)
    birth = Birth.objects.filter(person=person).first()
    death = Death.objects.filter(person=person).first()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    teal = colors.HexColor("#115e59")
    line_h = 0.32 * inch

    def section_header(label, y):
        c.setFillColor(teal)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(inch, y, label)
        c.setLineWidth(0.5)
        c.setStrokeColor(teal)
        c.line(inch, y - 3, width - inch, y - 3)
        return y - line_h

    def draw_field(label, value, y):
        c.setFillColor(teal)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(inch + 6, y, label)
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(2.6 * inch, y, str(value) if value else "N/A")
        return y - line_h

    # Header banner
    c.setFillColor(teal)
    c.rect(0, height - 1.1 * inch, width, 1.1 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 0.55 * inch, "Illinois Vital Records")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 0.82 * inch, "Individual Record Report")

    y = height - 1.4 * inch

    # Personal info
    y = section_header("Personal Information", y)
    full_name = (
        f"{person.first_name} {person.middle_name or ''} {person.last_name}".strip()
    )
    y = draw_field("Full Name:", full_name, y)
    y = draw_field("Sex:", person.get_sex_display() or "Unknown", y)
    y -= 0.1 * inch

    # Birth
    if birth:
        y = section_header("Birth", y)
        y = draw_field("Date:", birth.birth_date, y)
        y = draw_field("City:", birth.birth_city, y)
        y = draw_field("County:", birth.birth_county, y)
        y -= 0.1 * inch

    # Death
    if death:
        y = section_header("Death", y)
        y = draw_field("Date:", death.death_date, y)
        y = draw_field("Age:", death.death_age, y)
        y = draw_field("City:", death.death_city, y)
        y = draw_field("County:", death.death_county, y)
        y -= 0.1 * inch

    # Family
    y = section_header("Family", y)
    mother_str = (
        f"{person.mother.first_name} {person.mother.last_name}"
        if person.mother
        else "N/A"
    )
    father_str = (
        f"{person.father.first_name} {person.father.last_name}"
        if person.father
        else "N/A"
    )
    y = draw_field("Mother:", mother_str, y)
    y = draw_field("Father:", father_str, y)

    spouses = person.spouses()
    spouses_str = (
        ", ".join(f"{s.first_name} {s.last_name}" for s in spouses)
        if spouses
        else "N/A"
    )
    y = draw_field("Spouses:", spouses_str, y)

    children = person.children()
    children_str = (
        ", ".join(f"{ch.first_name} {ch.last_name}" for ch in children)
        if children
        else "N/A"
    )
    y = draw_field("Children:", children_str, y)

    # Footer
    c.setFillColor(teal)
    c.rect(0, 0, width, 0.45 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawCentredString(
        width / 2, 0.17 * inch, "Illinois Vital Records — Genealogical Research System"
    )

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{person.last_name}_{person.first_name}_record.pdf"'
    )
    return response


def home(request):
    return render(request, "home.html")


def our_mission(request):
    return render(request, "our_mission.html")


def glossary(request):
    return render(request, "glossary.html")
