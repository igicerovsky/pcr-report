"""PCR reporting script
"""


def well2idx(well_id):
    """Convert well id string to indices

    Parameters:
    -----------
    well_id : string
        Conatenated well identification

    Returns:
    tuple(string, int)
        Splitted row and column identification
    """
    wr = well_id[0]
    wc = int(well_id[1:])
    return wr, wc
