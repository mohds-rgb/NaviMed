# Pharmacy Duty Operations

## Workflow

```text
draft → submitted → verified → published → active → expired
```

The current owner policy uses manual admin entry. Submission alone never makes a schedule public.

## Required fields

Source, status, effective date, verification timestamp, verifying administrator, last-updated timestamp, city, branch and duty window.

## Freshness

A schedule is considered current only for its selected duty date. The default application timezone is `Asia/Damascus`; the midnight boundary is configurable and must be validated before production.

## Corrections

Corrections preserve historical records and create an audit trail.
