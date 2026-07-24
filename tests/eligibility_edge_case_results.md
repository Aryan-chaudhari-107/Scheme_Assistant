# Phase 4.5 - Eligibility Edge Case Test Results

## Borderline age 18 (Atal Pension Yojana, range 18-40)

```
Expected: likely_eligible | Actual: likely_eligible | PASS
Reasons: []
```

## Borderline age 40 (Atal Pension Yojana, range 18-40)

```
Expected: likely_eligible | Actual: likely_eligible | PASS
Reasons: []
```

## Borderline age 17 (Atal Pension Yojana, range 18-40)

```
Expected: likely_not_eligible | Actual: likely_not_eligible | PASS
Reasons: ['age 17 is below minimum age 18']
```

## Borderline age 41 (Atal Pension Yojana, range 18-40)

```
Expected: likely_not_eligible | Actual: likely_not_eligible | PASS
Reasons: ['age 41 is above maximum age 40']
```

## Borderline income Rs. 900,000 (PMAY-Urban, cutoff Rs. 9,00,000)

```
Expected: likely_eligible | Actual: likely_eligible | PASS
Reasons: []
```

## Borderline income Rs. 900,001 (PMAY-Urban, cutoff Rs. 9,00,000)

```
Expected: likely_not_eligible | Actual: likely_not_eligible | PASS
Reasons: ['income 900001 exceeds limit 900000']
```

## Multi-match profile (general adult, age 30, income 1.5L, no pucca house)

```
Number of schemes marked likely_eligible: 5
Schemes: ['atal-pension-yojana', 'pm-jan-dhan-yojana', 'pm-jeevan-jyoti-bima-yojana', 'pm-suraksha-bima-yojana', 'pmay-urban']
PASS (matches multiple schemes as expected)
```

## No/near-no-match profile (high income, govt employee, owns house, tax payer)

```
Number of schemes marked likely_eligible: 3
Schemes: ['pm-jan-dhan-yojana', 'pm-jeevan-jyoti-bima-yojana', 'pm-suraksha-bima-yojana']
PASS (correctly near-zero matches)
Note: any remaining matches should be genuinely universal, no-restriction schemes (e.g. PM Jan Dhan Yojana), which is correct behavior, not a bug.
```

## check_manually trigger: NSAP Old Age Pension (age 65, otherwise clean profile)

```
Status: check_manually | PASS
Explanation: Thank you for checking your eligibility for the Indira Gandhi National Old Age Pension Scheme. Because this scheme requires verification against specific BPL or SECC-2011 household records rather than just self-reported income, we cannot confirm your eligibility automatically. We recommend visiting your local government office or Panchayat to have your status manually verified against official records.
PASS (explanation communicates ambiguity, not a guess)
```

## check_manually trigger: PMAY-Gramin, houseless profile (owns_pucca_house=False)

```
Status: check_manually | Expected: check_manually | PASS
Reasons: ['Requires appearance in SECC 2011 / Awaas+ survey data verified by the gram sabha - not determinable from self-reported fields alone.']
```

## Regression check (Phase 4.5 fix): PMAY-Gramin, profile OWNS a pucca house

```
Status: likely_not_eligible | Expected: likely_not_eligible | PASS
Reasons: ['scheme excludes applicants who already own a pucca house']
```
