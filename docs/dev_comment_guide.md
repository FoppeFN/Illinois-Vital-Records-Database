# How to Use Comment Utilities

## Functions

- add_comment(person, fields):
    - person is a Person object from the database. This is what the comment is connected to internally.
    - fields is a dictionary of field, value pairs that should be filled as described below:

| Field | Value |
| --- | --- |
| comment_content | The comment content/text |
| commenter_name | The name of the commenter (optional) |
| commenter_email | The email of the commenter (optional) |