# Eligibility Questionnaire Design (Phase 4.1)

## Finalized user profile fields

| # | Field | Type | Values |
|---|-------|------|--------|
| 1 | `age` | numeric | 0-120 |
| 2 | `annual_family_income` | numeric | Rs., 0+ |
| 3 | `state` | dropdown | Gujarat, Other |
| 4 | `occupation` | dropdown | Farmer, Artisan/Craftsperson, Small Business Owner/Entrepreneur, Student, Unorganised Sector Worker, Homemaker, Government Employee, Other |
| 5 | `gender` | dropdown | Female, Male, Other |
| 6 | `social_category` | dropdown | General, OBC/SEBC, SC, ST, EBC, Minority |
| 7 | `marital_status` | dropdown | Unmarried, Married, Widowed |
| 8 | `owns_pucca_house` | boolean | Yes/No |
| 9 | `is_income_tax_payer` | boolean | Yes/No |
| 10 | `has_girl_child_under_10` | boolean | Yes/No |
| 11 | `is_pregnant_or_recent_mother` | boolean | Yes/No |

11 fields total - kept deliberately short since every extra question in a
real questionnaire increases drop-off.

## Cross-check: which fields are actually used by which schemes

| Field | Schemes that key off it |
|-------|--------------------------|
| `age` | atal-pension-yojana, e-shram, ganga-swaroop-yojana, nsap-old-age-pension, pm-fasal-bima-yojana, pm-jan-dhan-yojana, pm-jeevan-jyoti-bima-yojana, pm-matru-vandana-yojana, pm-mudra-yojana, pm-suraksha-bima-yojana, pm-ujjwala-yojana, pm-vishwakarma-yojana, sukanya-samriddhi-yojana, vahli-dikri-yojana, manav-garima-yojana |
| `annual_family_income` | ayushman-bharat-pmjay*, gujarat-post-matric-scholarship, manav-garima-yojana, mukhyamantri-gruh-yojana, nsp-post-matric-scholarship, nsp-pre-matric-scholarship, pmay-urban, vahli-dikri-yojana, ganga-swaroop-yojana |
| `state` | ganga-swaroop-yojana, gujarat-post-matric-scholarship, manav-garima-yojana, mukhyamantri-gruh-yojana, vahli-dikri-yojana (all Gujarat-only schemes) |
| `occupation` | pm-kisan, pm-fasal-bima-yojana, pm-kusum, e-shram, pm-mudra-yojana, pm-vishwakarma-yojana, manav-garima-yojana, nsp-pre-matric-scholarship, nsp-post-matric-scholarship, gujarat-post-matric-scholarship (all "student") |
| `gender` | pm-ujjwala-yojana (women), pm-matru-vandana-yojana (women), ganga-swaroop-yojana (widowed women) |
| `social_category` | nsp-pre-matric-scholarship, nsp-post-matric-scholarship, gujarat-post-matric-scholarship, manav-garima-yojana (all require SC/ST/OBC/EBC/Minority) |
| `marital_status` | ganga-swaroop-yojana (widow pension - requires widowed status) |
| `owns_pucca_house` | pmay-urban, pmay-gramin, mukhyamantri-gruh-yojana (all exclude existing pucca-house owners) |
| `is_income_tax_payer` | pm-kisan, atal-pension-yojana, e-shram (all explicitly exclude income tax payers) |
| `has_girl_child_under_10` | sukanya-samriddhi-yojana, vahli-dikri-yojana |
| `is_pregnant_or_recent_mother` | pm-matru-vandana-yojana |

**Checkpoint met:** every field maps to at least one real eligibility
criterion (several map to 5+ schemes each).

## Schemes flagged as NOT fully capturable by simple structured fields

Per the guide's explicit ask, two schemes have eligibility criteria that
depend on external verification our 11 fields can't reliably substitute for:

- **`ayushman-bharat-pmjay`** - true eligibility is based on **SECC 2011
  deprivation category** (a specific government household classification),
  not simply "low income." We approximate this using `annual_family_income`
  as a rough proxy (the guide's own `eligibility_rules.max_income` does the
  same), but this WILL produce false positives/negatives for households
  near the boundary. The matching logic (Phase 4.3) will show this scheme
  as "possibly eligible - please verify SECC status" rather than a hard yes.
- **`pmay-gramin`** - eligibility depends on whether the household appears
  in the **SECC 2011 / Awaas+ survey data**, verified by the gram sabha -
  this is a lookup against a specific government database, not something
  a self-reported questionnaire field can determine. Same "possibly
  eligible - please verify" treatment applies.

Both will still be included in results (never silently dropped), just
labeled as needing external verification rather than a confident match.