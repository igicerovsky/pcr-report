# PCR report generation

## TODO

- e2e test
- HT2, check for multiple targets
- Specification togetther with Fabian & Anja
  - Config folder content
  - Decimal digits format
  - File naming convention
    - base folder (? doesn't matter if analysis file is given as input)
    - analysis exported results file `230811_GN004773-019_20230811_100101_999.csv`
    - output names
      - final `230811_GN004773-019-final.xlsx`
      - detailed `230811_GN004773-019-data_analysis.xlsx`
  - Configuration (files, config)
    - pre-dilutions file format
- Next steps ???

## DONE

### KW48-27.11.2023

- deploy on Anjas computer
- `_conc` file as `.xlsx`

### KW48-20.11.2023

- `pcrep` module
- `report_gen.py` script
- decimal delimitrer
- preparing for specification (naming, config files, decimal symbol)

### pre-KW47-20.11.2023

- join all comments for given target
- warning limits
  - `for information only`
  - strikethrough text if within warning limits- columns order in final table
  - values together, comments ater
- droplets comment: `<10000`
