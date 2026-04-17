# Illinois Vitality Archive

## Overview

**Illinois Vitality Archive** is an interactive web-based database for exploring vital records within the state of Illinois. The system simulates a real-world genealogical archive using mock data, allowing users to search, navigate, and analyze relationships between individuals and their associated records.

The application is built using Django and emphasizes relational data modeling, flexible search functionality, and administrative data management.

> **Note:** All data in this system is synthetic and does not represent real individuals.

---

## Features

* 🔍 Searchable birth, death, and marriage records
* 👤 Person-centric data model with relational linking
* 🧬 Family relationship discovery (parents, siblings, spouses, children)
* 🧠 Fuzzy search using trigram similarity
* 🧩 Wildcard search support (`%`, `_`)
* 🗺️ Location-based filtering (county, city)
* 📝 Comment system (admin-moderated)
* ⚙️ Full Django admin interface with enhanced navigation
* 💾 Exportation of records (`CSV`, `PDF`)

---

## System Architecture

### Core Concept

The system is built around a **Person-first data model**, where all vital records are linked to individuals. This enables aggregation of records and dynamic exploration of relationships.

### Stack

**Frontend**

* Django Templates
* Tailwind CSS
* HTMX

**Backend**

* Django ORM
* PostgreSQL (with `pg_trgm` extension)

---

## Data Model

### Person

Central entity representing an individual.

* Stores name and sex
* Self-referential parent relationships:

  * `mother`
  * `father`
* Derived relationships:

  * Children
  * Siblings
  * Spouses

---

### Birth / Death

Each record is linked to a `Person`.

**Fields include:**

* Date (birth or death)
* Location:

  * County
  * City
* Optional record image

---

### Marriage

Represents a relationship between two individuals.

* Links two `Person` instances (`spouse1`, `spouse2`)
* Enforces uniqueness of:

  * spouse pair + marriage date
* Automatically normalizes spouse ordering to prevent duplicates

---

### Location Models

* **County**
* **City** (linked to County)

---

### Comment

* Associated with a `Person`
* Stores user-submitted notes
* Includes moderation state (`seen_by_admin`)
* Visible only in the admin interface

---

## Search System

The archive provides a flexible and powerful search system across all record types.

### 1. Wildcard Search

Custom wildcard support:

* `%` → matches **multiple characters**
* `_` → matches **a single character**

Examples:

```
Sm%th → Smith, Smyth
J_hn → John, Juhn
```

---

### 2. Fuzzy Search

Uses PostgreSQL trigram similarity (`pg_trgm`):

* Enables approximate name matching
* Configurable similarity threshold
* Applied to first, middle, and last names

---

### 3. Relational Filtering

Search queries span multiple related models:

* Person ↔ Birth / Death / Marriage
* Location filtering (County, City)
* Dual-person matching for marriages

---

### 4. Date Variance Filtering

Supports approximate year matching:

```
Search Year: 1900
Variance: 5

→ Matches records from 1895 to 1905
```

---

### 5. Post-query Narrowing

Additional filtering using `icontains` across:

* Direct model fields
* Related fields (one level deep)

---

## Mock Data Generation

The archive is populated using a custom procedural generation system designed to simulate realistic genealogical structures and demographic patterns.

### Overview

Data generation is centered around constructing **family trees** using probabilistic rules. The system produces interconnected individuals with consistent relationships, life events, and geographic data.

Each run generates:

* A network of people
* Parent-child relationships
* Marriages
* Birth and death records
* Location assignments

---

### Core Concepts

* **Child Cluster (CC)**
  A group of siblings sharing the same parents.

* **Partnered with Children Probability (PCP)**
  Probability that an individual has a partner and children (~69%).

* **Child Distribution (CD)**
  Number of children per couple, modeled as a normal distribution:

  * Mean: 2
  * Standard deviation: 1.5
  * Clamped to a maximum

* **Family Tree Depth Limit (FTDL)**
  Maximum generational depth.

* **Sibling-Partner Depth Limit (SPDL)**
  Limits expansion through in-law relationships.

---

### Generation Process

The algorithm builds a family tree recursively:

1. Generate an initial sibling group (root cluster).
2. Create parents for that group.
3. For each individual:

   * With probability (PCP), assign a partner.
   * Generate children using the child distribution.
4. Expand:

   * Parents (older generation)
   * Children (younger generation)
   * Siblings and in-law families
5. Repeat recursively until:

   * Family Tree Depth Limit (FTDL) is reached
   * Sibling-Partner Depth Limit (SPDL) is reached

This produces a branching, multi-generational structure.

---

### Person Generation

Each individual is assigned:

* Name (via Faker)
* Sex (M/F/U with small probability of unknown)
* Birth date (based on generational offset)
* Death date (derived from age distribution)
* Birth/death location (county + city)
* Parent relationships
* Children list
* Marriage status

Age is sampled from a normal distribution and used to derive realistic death dates.

---

### Marriage Logic

* Individuals are paired based on probability
* Marriage dates are generated relative to birth (~age 16–22)
* Duplicate marriages are prevented
* Last names follow historical conventions:

  * Children inherit father's surname
  * Married women adopt spouse’s surname

---

### Post-processing

After generation:

* Last names are normalized across generations
* Family consistency is enforced
* Seed values ensure reproducibility
* Data is exported to structured JSON

---

### Realism Assumptions

The generator loosely reflects early 20th-century patterns:

* Low divorce rates
* Patrilineal surnames
* Minimal surname variation (e.g., hyphenation is rare)
* Unknown-sex individuals do not form families

---

## User Guide

### Searching Records

Users can search using:

* Name (first, middle, last)
* Location (county, city)
* Dates (with optional variance)
* Wildcards or fuzzy matching

---

### Viewing Records

Each record detail page includes:

* Core record data
* Linked person profile
* Family relationships:

  * Parents
  * Siblings
  * Spouses
  * Children

---

### Comments

Users can submit comments on records. These are:

* Stored in the system
* Visible only to administrators
* Used for moderation and annotation

---

## Admin Interface

The Django admin panel provides full control over all data with enhanced usability features:

* 🔗 Cross-linked records (Person ↔ Birth / Death / Marriage)
* 📎 Direct navigation between related entities
* 📊 Custom list displays for readability
* ⚡ HTMX-powered comment moderation:

  * Mark comments as seen without page reload
  * Toggle comment state dynamically

---

## Design Decisions

### Person-Centric Schema

All records are anchored to a `Person`, allowing flexible relationship traversal and aggregation.

---

### Regex-Based Wildcard System

Wildcard queries are converted into regular expressions for more expressive matching than SQL `LIKE`.

---

### Trigram Indexing (GIN)

PostgreSQL GIN indexes with trigram operators improve fuzzy search performance.

---

### Marriage Normalization

Spouse ordering is enforced to prevent duplicate entries for the same pair.

---

## Future Improvements

* Add public visibility controls for comments
* Expand search to include additional record types
* Introduce data export functionality
* Improve frontend visualization of family trees

---

## Setup

### Clone the Project Locally

```
git clone https://github.com/FoppeFN/Illinois-Vitality-Archive/tree/main
cd project
```

### Create Custom Environment File

Inside the project directory, create a file called `.env` containing the following:

```
DJANGO_SUPERUSER_PASSWORD=<admin-password>
DJANGO_SUPERUSER_USERNAME=<admin-username>
DJANGO_SUPERUSER_EMAIL=IllinoisVitalityArchive@gmail.com
POSTGRES_DB=IIVRDAPPDB
POSTGRES_USER=IIVRDUSER
POSTGRES_PASSWORD=IIVRDPASSWORDSECRET
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=IIVRDSENIORDESIGN
DJANGO_DEBUG=1
```

### Build the Docker Environment

```
docker compose up --build
```

### Validate and Use

- Navigate to `http://localhost:8000/` in your web browser.
- If you see the site, you have set up the environment properly.
- To view the admin page, visit `http://localhost:8000/admin/` and use the username/password [you specified](#create-custom-environment-file) in `.env`.

### Populating the Database

Follow the [data generation guide](docs/data_gen_guide.md) to prepare the database to be populated.

---

## Continuous Integration

This project uses GitHub Actions to enforce automated quality checks on every push and pull request to the `main` branch.

### Quality Gates

The pipeline performs the following checks:

- Linting and formatting with ruff
- Static type checking with mypy (non-blocking)
- Security analysis with bandit (non-blocking)
- Testing with coverage using pytest + coverage
    - Minimum coverage threshold: 50%

---

## Other Information

Other useful information can be found in the [docs/](docs/) folder.

---

## Authors

- Sponsor: Mera Kachgal `mkachgal1@proton.me`
- Team:
    - Zachariah Brincken
    - Ian Dunn
    - Nicholas Foppe
    - Marquis Pritchett

---
