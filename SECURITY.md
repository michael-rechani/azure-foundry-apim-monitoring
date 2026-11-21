# Security policy

## Reporting a vulnerability

Please report security issues privately using
[GitHub private vulnerability reporting](https://github.com/michael-rechani/azure-foundry-apim-monitoring/security/advisories/new)
instead of opening a public issue.

## Do not post customer data

This repository is public. Do not include any of the following in issues, pull
requests, commits, or screenshots:

- Subscription, tenant, resource group, or resource IDs from a real environment
- APIM subscription names or keys, or any API keys or tokens
- Endpoint hostnames, workspace names, or deployment names that identify a
  customer
- Screenshots or exported workbook data from a customer environment

Use placeholder names such as `customer-a` instead.

## Scope

The workbook is read-only. It queries Azure Monitor metrics and Log Analytics
and deploying the ARM template only creates or updates one Workbook resource.
Users need Reader access to the resources and workspace they query.
