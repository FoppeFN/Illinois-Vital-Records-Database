from records.models import Comment


def add_comment(person, fields):
    comment_content = fields.get("comment_content", "").strip()

    if comment_content == "":
        return

    comment = Comment.objects.create(person=person, comment_content=comment_content)

    commenter_name = fields.get("commenter_name", None)
    commenter_email = fields.get("commenter_email", None)

    if commenter_name is not None:
        comment.commenter_name = commenter_name

    if commenter_email is not None:
        comment.commenter_email = commenter_email

    comment.save()
