# Power BI Report Creation Proof

Generated: 2026-07-17 21:21 Africa/Johannesburg

## Created Report

- Workspace: `Apollis`
- Workspace ID: `e515bafe-7290-4832-ae1d-514be43a9d87`
- Semantic model: `Leatt Fabric BI ML Semantic Model 202607171909`
- Semantic model ID: `9ee6f8a0-aec0-48ff-a44c-15985f3bd4bc`
- Report name: `Power BI executive report proof redacted`
- Report ID: `report-id-redacted`
- Report URL: `https://app.powerbi.com/groups/e515bafe-7290-4832-ae1d-514be43a9d87/reports/report-id-redacted/ReportSection`

## How It Was Created

The report was created through the Microsoft Fabric Report Create API:

`POST https://api.fabric.microsoft.com/v1/workspaces/e515bafe-7290-4832-ae1d-514be43a9d87/reports`

The payload used PBIR report definition parts and bound the report to the existing Power BI semantic model using:

`semanticmodelid=9ee6f8a0-aec0-48ff-a44c-15985f3bd4bc`

## Report Pages

- Executive Overview
- Marketing And SEO
- ML Return Risk
- Fabric Governance Proof

## Visual Design

- Monthly revenue line chart
- Category revenue and margin charts
- Executive KPI table
- Channel revenue, ROAS, spend and returns visuals
- ML return-risk visuals by risk band and category
- Fabric proof and ML metric tables
- Monthly row-count and return-trend visuals

## API Result

The Fabric long-running operation completed successfully:

- Status: `Succeeded`
- Percent complete: `100`
- Operation ID: `cbce1a2f-0713-4a92-86e4-094385938410`

## Service Export Evidence

After the report was created, Fabric Fabric capacity was briefly resumed and a Power BI export job was tested.

- Export status: `Succeeded`
- Export percent complete: `100`
- Export caveat: the service export rendered Power BI loading screens rather than useful page visuals, so those blank images were not included in the Git proof package.
- Browser caveat: opening the report URL in the local browser reached a Power BI sign-in prompt. A signed-in browser session is required for visual review and manual screenshot capture.

Fabric Fabric capacity was suspended again after the export and verified as:

- Capacity: `fabric-capacity-redacted`
- State: `Paused`

## Source Definition

Local PBIR report definition folder:

`outputs/fabric_powerbi_reports/Power BI executive report proof redacted.Report`
