# Azure Data Factory Exports

Place Azure Data Factory Git-mode JSON or exported ARM templates here.

For classic ADF portal export, copy ARM template files into:

`azure-export/adf-arm-template/`

For ADF Git mode, include:

- `pipeline/*.json`
- `dataset/*.json`
- `linkedService/*.json`
- `trigger/*.json`

Secrets must be parameterized or removed before committing.
