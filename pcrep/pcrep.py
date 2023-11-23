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


def result_fn(conc, dil, a=20.0, b=2.0):
    """Compute results

    Parameters:
    conc : float
    dil : float
        final dilution factor of the sample
    a : float
        ddPCR Volume 20 µL
    b : float
        Sample volume in the ddPCR reaction 2 µL
    """
    return ((a * conc) * (1000.0 / b)) * dil
