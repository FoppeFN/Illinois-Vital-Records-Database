from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Birth, City, Comment, County, Death, Marriage, Person

ext_color = "darkorange"


# Register your models here.


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    autocomplete_fields = ["mother", "father"]

    search_fields = ["id", "last_name", "first_name", "middle_name"]

    readonly_fields = (
        "view_birth_link",
        "view_death_link",
        "view_marriage_link",
        "view_comments_link",
    )

    list_display = ["id", "last_name", "first_name", "middle_name"]

    list_display_links = ["id", "last_name", "first_name", "middle_name"]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "last_name",
                    "first_name",
                    "middle_name",
                    "sex",
                    "mother",
                    "father",
                )
            },
        ),
        (
            "Related Records",
            {
                "fields": (
                    "view_birth_link",
                    "view_death_link",
                    "view_marriage_link",
                    "view_comments_link",
                )
            },
        ),
    )

    def view_birth_link(self, obj):
        url = reverse("admin:records_birth_changelist") + f"?person__id__exact={obj.id}"
        return format_html(
            '<a href="{}" style="color:{}">View Birth Record(s)</a>', url, ext_color
        )

    def view_death_link(self, obj):
        url = reverse("admin:records_death_changelist") + f"?person__id__exact={obj.id}"
        return format_html(
            '<a href="{}" style="color:{}">View Death Record(s)</a>', url, ext_color
        )

    def view_marriage_link(self, obj):

        m = Marriage.objects.filter(spouse1=obj)
        if m.exists():
            url = (
                reverse("admin:records_marriage_changelist")
                + f"?spouse1__id__exact={obj.id}"
            )
        else:
            url = (
                reverse("admin:records_marriage_changelist")
                + f"?spouse2__id__exact={obj.id}"
            )

        return format_html(
            '<a href="{}" style="color:{}">View Marriage Record(s)</a>', url, ext_color
        )

    def view_comments_link(self, obj):
        url = (
            reverse("admin:records_comment_changelist") + f"?person__id__exact={obj.id}"
        )
        return format_html(
            '<a href="{}" style="color:{}">View Comments</a>', url, ext_color
        )

    view_comments_link.short_description = "Comments"
    view_birth_link.short_description = "Birth"
    view_death_link.short_description = "Death"
    view_marriage_link.short_description = "Marriage"


@admin.register(Birth)
class BirthAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person"]

    search_fields = [
        "person__last_name",
        "person__first_name",
        "person__middle_name",
        "birth_date",
        "birth_county__county_code",
        "birth_county__county_name",
        "birth_city__city_name",
    ]

    list_display = [
        "id",
        "last_name",
        "first_name",
        "middle_name",
        "birth_date",
        "birth_county_name",
        "birth_city_name",
        "related_person",
    ]

    list_display_links = list_display

    def birth_county_name(self, obj):
        url = reverse(
            "admin:records_county_change", args=[obj.birth_county.county_code]
        )
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.birth_county.county_name,
        )

    def birth_city_name(self, obj):
        url = reverse("admin:records_city_change", args=[obj.birth_city.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.birth_city.city_name,
        )

    def last_name(self, obj):
        return obj.person.last_name

    def first_name(self, obj):
        return obj.person.first_name

    def middle_name(self, obj):
        return obj.person.middle_name

    def related_person(self, obj):
        url = reverse("admin:records_person_change", args=[obj.person.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>', url, ext_color, obj.person.id
        )

    birth_county_name.short_description = "County"
    birth_city_name.short_description = "City"
    last_name.short_description = "Last"
    first_name.short_description = "First"
    middle_name.short_description = "Middle"
    related_person.short_description = "Person ID"


@admin.register(Death)
class DeathAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person"]

    search_fields = [
        "person__last_name",
        "person__first_name",
        "person__middle_name",
        "death_date",
        "death_county__county_code",
        "death_county__county_name",
        "death_city__city_name",
    ]

    list_display = [
        "id",
        "last_name",
        "first_name",
        "middle_name",
        "death_date",
        "death_county_name",
        "death_city_name",
        "related_person",
    ]

    list_display_links = list_display

    def death_county_name(self, obj):
        url = reverse(
            "admin:records_county_change", args=[obj.death_county.county_code]
        )
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.death_county.county_name,
        )

    def death_city_name(self, obj):
        url = reverse("admin:records_city_change", args=[obj.death_city.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.death_city.city_name,
        )

    def last_name(self, obj):
        return obj.person.last_name

    def first_name(self, obj):
        return obj.person.first_name

    def middle_name(self, obj):
        return obj.person.middle_name

    def related_person(self, obj):
        url = reverse("admin:records_person_change", args=[obj.person.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>', url, ext_color, obj.person.id
        )

    death_county_name.short_description = "County"
    death_city_name.short_description = "City"
    last_name.short_description = "Last"
    first_name.short_description = "First"
    middle_name.short_description = "Middle"
    related_person.short_description = "Person ID"


@admin.register(Marriage)
class MarriageAdmin(admin.ModelAdmin):
    autocomplete_fields = ["spouse1", "spouse2"]

    search_fields = [
        "spouse1__last_name",
        "spouse1__first_name",
        "spouse1__middle_name",
        "spouse2__last_name",
        "spouse2__first_name",
        "spouse2__middle_name",
        "marriage_date",
        "marriage_county__county_code",
        "marriage_county__county_name",
        "marriage_city__city_name",
    ]

    list_display = [
        "id",
        "spouse1",
        "spouse2",
        "marriage_date",
        "marriage_county_name",
        "marriage_city_name",
        "sp1_id",
        "sp2_id",
    ]

    list_display_links = list_display

    def marriage_county_name(self, obj):
        url = reverse(
            "admin:records_county_change", args=[obj.marriage_county.county_code]
        )
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.marriage_county.county_name,
        )

    def marriage_city_name(self, obj):
        url = reverse("admin:records_city_change", args=[obj.marriage_city.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.marriage_city.city_name,
        )

    def sp1_id(self, obj):
        url = reverse("admin:records_person_change", args=[obj.spouse1.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>', url, ext_color, obj.spouse1.id
        )

    def sp2_id(self, obj):
        url = reverse("admin:records_person_change", args=[obj.spouse2.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>', url, ext_color, obj.spouse2.id
        )

    marriage_county_name.short_description = "County"
    marriage_city_name.short_description = "City"
    sp1_id.short_description = "Spouse1 ID"
    sp2_id.short_description = "Spouse2 ID"


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    search_fields = ["county_code", "county_name"]

    list_display = ["county_code", "county_name"]

    list_display_links = list_display


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    autocomplete_fields = ["county"]

    search_fields = ["county__county_code", "county__county_name", "city_name"]

    list_display = ["id", "city_name", "county_name", "county_code"]

    list_display_links = list_display

    def county_name(self, obj):
        url = reverse("admin:records_county_change", args=[obj.county.county_code])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.county.county_name,
        )

    def county_code(self, obj):
        url = reverse("admin:records_county_change", args=[obj.county.county_code])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>',
            url,
            ext_color,
            obj.county.county_code,
        )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    autocomplete_fields = ["person"]

    class Media:
        js = (
            "https://unpkg.com/htmx.org@1.9.12",
            "/static/admin/htmx_csrf.js",
        )

    search_fields = ["comment_name", "comment_email", "person__id"]

    readonly_fields = ["show_content"]
    list_filter = ["seen_by_admin"]
    list_display = [
        "id_seen",
        "creation_time_seen",
        "commenter_name_seen",
        "commenter_email_seen",
        "related_person",
        "seen",
    ]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "commenter_name",
                    "commenter_email",
                    "creation_time",
                    "person",
                    "comment_content",
                )
            },
        ),
        ("Content", {"fields": ("show_content", "seen_by_admin")}),
    )

    def mark_seen(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        comment.seen_by_admin = True
        comment.save()
        return HttpResponse("")

    def build_std_link(self, obj, hyperlink):
        url = reverse("admin:mark_seen", args=[obj.id])
        change_url = reverse("admin:records_comment_change", args=[obj.id])

        return format_html(
            """
            <a href="{}"
            hx-post="{}"
            hx-trigger="click"
            hx-swap="none"
            hx-on="click: event.preventDefault(); window.location.href='{}';">
                {}
            </a>
            """,
            change_url,
            url,
            change_url,
            hyperlink,
        )

    def id_seen(self, obj):
        return self.build_std_link(obj, obj.id)

    def commenter_name_seen(self, obj):
        return self.build_std_link(obj, obj.commenter_name)

    def commenter_email_seen(self, obj):
        return self.build_std_link(obj, obj.commenter_email)

    def creation_time_seen(self, obj):
        return self.build_std_link(obj, obj.creation_time.strftime("%Y-%m-%d %H:%M:%S"))

    def related_person(self, obj):
        url = reverse("admin:records_person_change", args=[obj.person.id])
        return format_html(
            '<a href="{}" style="color:{}">{}</a>', url, ext_color, obj.person
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "toggle-seen/<int:comment_id>/",
                self.admin_site.admin_view(self.toggle_seen),
                name="toggle_seen",
            ),
            path(
                "mark-seen/<int:comment_id>/",
                self.admin_site.admin_view(self.mark_seen),
                name="mark_seen",
            ),
        ]
        return custom_urls + urls

    def toggle_seen(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)

        comment.seen_by_admin = not comment.seen_by_admin
        comment.save()

        icon = "⬤" if comment.seen_by_admin else "◯"
        color = "green" if comment.seen_by_admin else "red"

        url = reverse("admin:toggle_seen", args=[comment.id])

        return HttpResponse(f'''
            <span
                hx-post="{url}"
                hx-target="this"
                hx-swap="outerHTML"
                style="cursor: pointer; color: {color};"
            >
                {icon}
            </span>
        ''')

    def seen(self, obj):
        url = reverse("admin:toggle_seen", args=[obj.id])

        icon = "⬤" if obj.seen_by_admin else "◯"
        color = "green" if obj.seen_by_admin else "red"

        return format_html(
            """
            <span
                hx-post="{}"
                hx-target="this"
                hx-swap="outerHTML"
                style="cursor: pointer; color: {};"
            >
                {}
            </span>
            """,
            url,
            color,
            icon,
        )

    def show_content(self, obj):
        return format_html(
            """
            <div style="
                max-width: 600px;
                min-height: 40px;
                max-height: 200px;
                padding: 10px 12px;
                border: 1px solid var(--border-color, #ccc);
                border-radius: 4px;
                background: var(--darkened-bg, #f8f8f8);
                color: var(--body-fg, #333);
                white-space: pre-wrap;
                overflow-wrap: break-word;
                overflow-y: auto;
                line-height: 1.5;
                font-family: var(--font-family-primary, sans-serif);
                box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
            ">{}</div>
            """,
            obj.comment_content,
        )

    id_seen.short_description = "ID"
    commenter_name_seen.short_description = "Commenter Name"
    commenter_email_seen.short_description = "Commenter Email"
    creation_time_seen.short_description = "Creation Time"
    related_person.short_description = "Related Person"
    seen.short_description = "Seen"
    show_content.short_description = "Comment Content"
