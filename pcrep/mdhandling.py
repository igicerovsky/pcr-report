"""Conversion from markdown to PDF and DOCX

Convert markdown document to pdf or MS Word document using Pandoc. 
For MS Word conversion a reference document defining styles is needed, 
default reference location is defned in ./../data/config.json.
PDF conversion needs a pdf-engine which has to installed, 
see Prerequsities section in README.md.
"""

from os import path
import subprocess

# from .reportmd import save_md


def md2docx(pandoc_bin, reference_doc, md_filepath):
    """Converts md to docx

    Parameters
    ----------
    pandoc_bin : path_like
        path to pandoc exeutable.
    reference_doc : path_like
        path to docx reference doc defining styles.
    md_filepath : path_like
        path to md document to be converted
    """

    docx_path = path.splitext(md_filepath)[0] + '.docx'
    print('Generating Word {} from {}'.format(docx_path, md_filepath))
    report_dir = path.dirname(path.abspath(md_filepath))
    try:
        subprocess.run([pandoc_bin, '-o', docx_path,
                        '-f', 'markdown', '-t', 'docx',
                        '--resource-path', report_dir,
                        '--reference-doc', reference_doc,
                        md_filepath])
    except Exception as e:
        print(e)


def md2pdf(pandoc_bin, pdflatex_bin, md_filepath):
    """Converts md to pdf

    Parameters
    ----------
    pandoc_bin : path_like
        path to pandoc exeutable.
    pdflatex_bin : path_like
        path to pdf engine.
    md_filepath : path_like
        path to md document to be rendered
    """
    pdf_path = path.splitext(md_filepath)[0] + '.pdf'
    print(f'Generating PDF {pdf_path} from {md_filepath}')
    report_dir = path.dirname(path.abspath(md_filepath))
    try:
        subprocess.run([pandoc_bin, '-o', pdf_path,
                        '--resource-path', report_dir,
                        '--pdf-engine', pdflatex_bin,
                        md_filepath])
    except Exception as e:
        print(e)
