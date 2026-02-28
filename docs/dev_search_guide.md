# How to Search Records

## Filtered Search

### Filtered Search Parameters

These are the parameters for functions listed in [Filtered Search Functions](#filtered-search-functions).

- filters (dict): A dictionary of field, value pairs. See [Fields](#fields) for what is expected inside the dictionary.
- fuzzy (bool): A boolean value indicating whether or not name fields (first_name, middle_name, or last_name) should be discovered via fuzzy search. Fuzzy is false by default.

### Filtered Search Functions

- birth_search(filters, fuzzy)
    - Returns a Django QuerySet of Birth objects based on given [parameters](#filtered-search-parameters).
- death_search(filters, fuzzy)
    - Returns a Django QuerySet of Death objects based on given [parameters](#filtered-search-parameters).
- marriage_search(filters, fuzzy)
    - Returns a Django QuerySet of Marriage objects based on given [parameters](#filtered-search-parameters).

## Narrow Down Search

### Narrow Down Search Parameters

These are the parameters for the [narrow down function](#narrow-down-function).

- query (str): The string that will be searched for across all fields.
- objects (QuerySet): A Django QuerySet as returned by a [filtered search function](#filtered-search-functions).

### Narrow Down Function

- narrow_down(query, objects)
    - Returns a subset of the objects passed in based on the query passed in.

## Fields

The expected structure of [filters](#filtered-search-parameters) for any [filtered search function](#filtered-search-functions) to work properly. Note that no field, value pair is required and any/all can be left empty. All fields and values should be passed in as strings.

Additionally, [wildcards](#wildcards) can be used in values for name fields in the case of non-fuzzy searches. Wildcards will not break a fuzzy search, but may return unexpected results.

### Birth Record Search

| Field | Value |
| --- | --- |
| first_name | A person's first name. |
| middle_name | A person's middle name. |
| last_name | A person's last name. |
| county_name | The person's birth county's name. |
| city_name | The person's birth city's name. |
| birth_date | A person's birth date. |
| variance | The number of years of variance in birth date. |

### Death Record Search

| Field | Value |
| --- | --- |
| first_name | A person's first name. |
| middle_name | A person's middle name. |
| last_name | A person's last name. |
| county_name | The perons's death county's name. |
| city_name | The person's death city's name. |
| death_date | A person's death date. |
| variance | The number of years of variance in death date. |

### Marriage Record Search

| Field | Value |
| --- | --- |
| spouse1_first_name | The first name of spouse1 (spouse1 may be the bride or groom). |
| spouse1_middle_name | The middle name of spouse1. |
| spouse1_last_name | The last name of spouse1. |
| spouse2_first_name | The first name of spouse2 (spouse2 may be the bride or groom). |
| spouse2_middle_name | The middle name of spouse2. |
| spouse2_last_name | The last name of spouse2. |
| county_name | The marriage county name. |
| city_name | The marriage city name. |
| marriage_date | The date of marriage. |
| variance | The number of years of variance in marriage date. |

### Wildcards

| Wildcard | Use |
| --- | --- |
| _ (underscore) | Used to indicate a single unknown character (e.g., J_n could match Jon or Jan). |
| % | Used to indicate any number of unknown characters (e.g., J%n could match Jon, Jan, or John). |