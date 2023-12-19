import pandas as pd


def analysis_to_excel(df: pd.DataFrame, filename: str):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name="Sheet1")

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # Add some cell formats.
    fmt_fdl = workbook.add_format({"num_format": "0E+00"})
    fmt_dec2e = workbook.add_format({"num_format": "0.00E+00"})
    fmt_dec2f = workbook.add_format({"num_format": "0.00"})

    # Note: It isn't possible to format any cells that already have a format such
    # as the index or headers or any cells that contain dates or datetimes.

    # Set the column width and format.
    worksheet.set_column('D:D', 32)
    worksheet.set_column('E:E', 18, fmt_fdl)
    worksheet.set_column('F:F', 14, fmt_dec2f)
    worksheet.set_column('G:I', 14, fmt_dec2e)
    worksheet.set_column('J:J', None, fmt_dec2f)
    worksheet.set_column('K:K', 32)
    worksheet.set_column('L:O', 16)

    # Add a format.
    format_strike = workbook.add_format()
    format_strike.set_font_strikeout()
    rows = len(df.index)

    # Apply a conditional format to the required cell range.
    worksheet.conditional_format(f'F2:G{rows}',
                                 {'type':     'formula',
                                  'criteria': '=SEARCH("information", $K2)>0',
                                  'format':   format_strike})

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    print(f'Analysis exported to excel as {filename}')


def final_to_excel(df, filename):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name="Sheet1")

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # Add some cell formats.
    fmt_dec2e = workbook.add_format({"num_format": "0.00E+00"})

    # Note: It isn't possible to format any cells that already have a format such
    # as the index or headers or any cells that contain dates or datetimes.

    # Set the column width and format.
    worksheet.set_column('D:D', 32)
    worksheet.set_column('E:E', 18, fmt_dec2e)
    worksheet.set_column('F:F', 24, fmt_dec2e)
    worksheet.set_column('G:G', 32)
    worksheet.set_column('H:H', 32)

    # Add a format.
    format_strike = workbook.add_format()
    format_strike.set_font_strikeout()
    rows = len(df.index)

    # Apply a conditional format to the required cell range.
    worksheet.conditional_format(f'E2:E{rows}',
                                 {'type':     'formula',
                                  'criteria': '=SEARCH("information", $G2)>0',
                                  'format':   format_strike})
    worksheet.conditional_format(f'F2:F{rows}',
                                 {'type':     'formula',
                                  'criteria': '=SEARCH("information", $H2)>0',
                                  'format':   format_strike})

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()
    print(f'Final report exported to excel as {filename}')
