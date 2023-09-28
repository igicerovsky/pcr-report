# PCR  Report Generation

Python project for automatic report generation from PCR measurements.

## Prerequisities

To install python libraries use

```bash
pip install -r requirements.txt```
```

Install `pandoc` frpm [pandoc](https://pandoc.org/installing.html) website.  

Install `latex` from any of the [distributions](https://www.latex-project.org/get/#tex-distributions).  

## Buld distribution of `pcrep`

For experts only!  
To build a `pcrep` library execute following command:

```bash
python -m build --sdist --wheel
```

## Running the script

`DIR_NAME` is path to a folder with finished Hamilton analysis, e.g. `C:/work/report-gen/reports/230426_AAV9-ELISA_igi_GN004240-033`  
The working directory **must** contain following files in given format:  

- `[DATE]_[GN]_-_worklist-ELISA.xls`
- `[DATE]_[GN]_-_[PROTOCOL]_Parameters.csv`

where `[DATE]` is a date in format `%y%m%d` (*230801*)  
`[GN]` is analysis identifier (*GN004240-033*)  
`[PROTOCOL]` is a protocol name (*AAV9-ELISA*)

Examples:  
`230426_GN004240-033_-_worklist-ELISA.xls`  
`230426_GN004240-033_-_AAV9-ELISA_Parameters.csv`

### Running with exported photometer `txt` data

This is a prefered way to run the preocessing of the results and following report generation.

```bash
python report_gen.py ./DIR_NAME
```