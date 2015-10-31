def byte_range(data, start, end=None):
    """
    Returns data in the given byte range
    """
    if end:
        return data[start:end + 1]
    else:
        return data[start]
