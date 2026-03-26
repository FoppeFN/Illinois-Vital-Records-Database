from PIL import Image, ImageDraw, ImageFont
import io
import os
import random


def _get_font(bold=False, size=18):
    """Try to load a system serif font, fallback to default."""
    bold_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ]
    regular_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    paths = bold_paths if bold else regular_paths
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _draw_certificate_frame(draw, width, height, border_color, bg_color):
    """Draw outer and inner border."""
    draw.rectangle([15, 15, width - 15, height - 15], outline=border_color, width=5)
    draw.rectangle([25, 25, width - 25, height - 25], outline=border_color, width=2)


def _draw_header(draw, width, record_type, border_color):
    """Draw STATE OF ILLINOIS header and certificate title, return y after header."""
    title_font = _get_font(bold=True, size=30)
    subtitle_font = _get_font(bold=True, size=18)

    y = 60
    draw.text((width // 2, y), "STATE OF ILLINOIS", fill=border_color, font=title_font, anchor="mm")
    y += 44
    draw.text((width // 2, y), "DEPARTMENT OF PUBLIC HEALTH", fill=border_color, font=subtitle_font, anchor="mm")
    y += 34
    draw.text((width // 2, y), record_type, fill=border_color, font=title_font, anchor="mm")
    y += 28
    draw.line([45, y, width - 45, y], fill=border_color, width=3)
    draw.line([45, y + 6, width - 45, y + 6], fill=border_color, width=1)
    return y + 28


def _draw_fields(draw, fields, start_y, width, header_color, text_color):
    """Draw label/value pairs with separator lines, return final y."""
    label_font = _get_font(bold=True, size=15)
    value_font = _get_font(bold=False, size=15)
    y = start_y
    for label, value in fields:
        draw.text((60, y), label, fill=header_color, font=label_font)
        y += 22
        draw.text((60, y), str(value) if value else "Unknown", fill=text_color, font=value_font)
        y += 18
        draw.line([60, y + 4, width - 60, y + 4], fill=(190, 190, 175), width=1)
        y += 18
    return y


def _draw_footer(draw, width, height, border_color, reg_num):
    """Draw footer with registration number and signature line."""
    small_font = _get_font(bold=False, size=11)
    y_bottom = height - 120
    draw.line([45, y_bottom, width - 45, y_bottom], fill=border_color, width=1)
    draw.text((60, y_bottom + 14), f"File No.: {reg_num}", fill=(90, 90, 90), font=small_font)
    draw.text(
        (width // 2, y_bottom + 14),
        "Registrar's Signature: _______________________",
        fill=(90, 90, 90), font=small_font, anchor="mm"
    )
    draw.text(
        (width // 2, y_bottom + 38),
        "This is a true and correct copy of the record on file.",
        fill=(90, 90, 90), font=small_font, anchor="mm"
    )
    draw.text(
        (width // 2, y_bottom + 60),
        "Illinois Department of Public Health — Division of Vital Records",
        fill=(90, 90, 90), font=small_font, anchor="mm"
    )


def generate_birth_certificate_image(person, birth):
    """Return a PIL Image of a fake Illinois birth certificate."""
    width, height = 850, 1100
    bg_color = (255, 252, 235)
    border_color = (0, 80, 70)  # teal
    text_dark = (25, 25, 25)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    _draw_certificate_frame(draw, width, height, border_color, bg_color)
    y = _draw_header(draw, width, "CERTIFICATE OF LIVE BIRTH", border_color)

    name = f"{person.first_name} {person.middle_name or ''} {person.last_name}".strip()
    birth_date = str(birth.birth_date) if birth and birth.birth_date else "Unknown"
    birth_city = str(birth.birth_city) if birth and birth.birth_city else "Unknown"
    birth_county = (str(birth.birth_county) + " County") if birth and birth.birth_county else "Unknown"
    sex = person.get_sex_display() if person.sex else "Unknown"
    mother = f"{person.mother.first_name} {person.mother.last_name}" if person.mother else "Unknown"
    father = f"{person.father.first_name} {person.father.last_name}" if person.father else "Unknown"

    fields = [
        ("Full Name of Child:", name),
        ("Date of Birth:", birth_date),
        ("Place of Birth:", birth_city),
        ("County:", birth_county),
        ("Sex:", sex),
        ("Mother's Name:", mother),
        ("Father's Name:", father),
    ]

    _draw_fields(draw, fields, y, width, border_color, text_dark)

    raw = birth.birth_date if birth and birth.birth_date else None
    year = int(str(raw)[:4]) if raw else 1900
    reg_num = f"IL-B-{year}-{random.randint(10000, 99999)}"
    _draw_footer(draw, width, height, border_color, reg_num)

    return img


def generate_death_certificate_image(person, death):
    """Return a PIL Image of a fake Illinois death certificate."""
    width, height = 850, 1100
    bg_color = (255, 252, 235)
    border_color = (90, 20, 20)  # maroon
    text_dark = (25, 25, 25)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    _draw_certificate_frame(draw, width, height, border_color, bg_color)
    y = _draw_header(draw, width, "CERTIFICATE OF DEATH", border_color)

    name = f"{person.first_name} {person.middle_name or ''} {person.last_name}".strip()
    death_date = str(death.death_date) if death and death.death_date else "Unknown"
    death_city = str(death.death_city) if death and death.death_city else "Unknown"
    death_county = (str(death.death_county) + " County") if death and death.death_county else "Unknown"
    sex = person.get_sex_display() if person.sex else "Unknown"
    age = str(death.death_age) if death and death.death_age is not None else "Unknown"

    fields = [
        ("Full Name of Deceased:", name),
        ("Date of Death:", death_date),
        ("Place of Death:", death_city),
        ("County:", death_county),
        ("Sex:", sex),
        ("Age at Death:", age),
    ]

    _draw_fields(draw, fields, y, width, border_color, text_dark)

    raw = death.death_date if death and death.death_date else None
    year = int(str(raw)[:4]) if raw else 1900
    reg_num = f"IL-D-{year}-{random.randint(10000, 99999)}"
    _draw_footer(draw, width, height, border_color, reg_num)

    return img


def image_to_content_file(img, filename):
    """Convert a PIL Image to a Django ContentFile for saving to an ImageField."""
    from django.core.files.base import ContentFile
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return ContentFile(buffer.read(), name=filename)
