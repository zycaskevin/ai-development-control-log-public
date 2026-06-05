# Irreversible Operations Checklist

Before an AI agent performs any of the following actions, it must stop and ask for explicit user confirmation.

## Data

- [ ] Delete records
- [ ] Bulk update records
- [ ] Overwrite files or user-generated content
- [ ] Change retention, backups, or restore behavior

## Database

- [ ] Create / alter / drop tables
- [ ] Add or remove columns
- [ ] Run migrations
- [ ] Change constraints, indexes, or RLS policies

## Production

- [ ] Deploy to production
- [ ] Change production environment variables
- [ ] Modify DNS, routing, gateway, or webhook config
- [ ] Rotate or expose credentials

## Money

- [ ] Change payment logic
- [ ] Change billing, subscription, invoice, refund, or commission logic
- [ ] Change pricing or plan entitlements

## Security

- [ ] Change auth, roles, permissions, or access policies
- [ ] Modify secrets or token handling
- [ ] Disable validation or security checks

## Core Product Logic

- [ ] Change calculation formulas
- [ ] Change state machines
- [ ] Change user-visible decisions made by the product

## Required confirmation format

The agent should summarize:

1. What will change
2. Why it is needed
3. What can go wrong
4. How to roll back
5. The exact confirmation needed

Example:

> This changes the production billing calculation. It may affect real customer invoices. Rollback is commit `abc123` plus restoring the previous pricing config. Please confirm: “Proceed with billing logic change.”
