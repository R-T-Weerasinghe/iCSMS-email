def parse_to_list(v):
    if v is not None:
        return [x.strip() for x in v.split(',')]
    return v
