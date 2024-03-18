def sanitize_filename(filename): #method for cleaning up json filenames to allow local storage
    return "".join([c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename])