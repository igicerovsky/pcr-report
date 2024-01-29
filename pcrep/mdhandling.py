"""Conversion from markdown to PDF and DOCX

Convert markdown document to pdf or MS Word document using Pandoc. 
For MS Word conversion a reference document defining styles is needed, 
default reference location is defned in ./../data/config.json.
PDF conversion needs a pdf-engine which has to installed, 
see Prerequsities section in README.md.
"""

from pathlib import Path

from os import path
import subprocess
from subprocess import SubprocessError
from .typing import PathLike


def md2docx(pandoc_bin: PathLike, reference_doc: PathLike, md_filepath: PathLike):
    """Converts md to docx

    Parameters
    ----------
    pandoc_bin : PathLike
        Path to the pandoc executable.
    reference_doc : PathLike
        Path to the docx reference document defining styles.
    md_filepath : PathLike
        Path to the md document to be converted.
    """

    docx_path = path.splitext(md_filepath)[0] + '.docx'
    print('Generating Word {} from {}'.format(docx_path, md_filepath))
    report_dir = path.dirname(path.abspath(md_filepath))
    try:
        subprocess.run([pandoc_bin, '-o', docx_path,
                        '-f', 'markdown', '-t', 'docx',
                        '--resource-path', report_dir,
                        '--reference-doc', reference_doc,
                        md_filepath], check=False)
    except (SubprocessError,) as e:
        print(e)


def md2pdf(pandoc_bin: PathLike, pdflatex_bin: PathLike, md_filepath: PathLike):
    """Converts Markdown (md) file to PDF using Pandoc.

    Parameters
    ----------
    pandoc_bin : Union[str, Path]
        Path to the Pandoc executable.
    pdflatex_bin : Union[str, Path]
        Path to the PDF engine (e.g., pdflatex).
    md_filepath : Union[str, Path]
        Path to the Markdown file to be converted.

    Raises
    ------
    Exception
        If there is an error during the conversion process.

    Notes
    -----
    This function requires Pandoc and a PDF engine (e.g., pdflatex) to be installed on the system.
    The converted PDF file will be saved in the same directory as the input Markdown file, with the same name but with a .pdf extension.
    """

    pdf_path = Path(md_filepath).with_suffix('.pdf')
    print(f'Generating PDF {pdf_path} from {md_filepath}')
    report_dir = Path(md_filepath).parent
    try:
        subprocess.run([pandoc_bin, '-o', pdf_path,
                        '--resource-path', report_dir,
                        '--pdf-engine', pdflatex_bin,
                        md_filepath], check=False)
    except (SubprocessError,) as e:
        print(e)
