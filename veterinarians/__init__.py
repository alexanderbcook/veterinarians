def extract(selector, allowMiss=True, allowEmpty=True):
    '''Call extract() on the argument, strip out all whitespace, and return the first element that
    actually contains some data. Basically a replacement for x.extract()[0].strip() but a bit better
    when the text nodes are separated by a comment or something.'''
    if len(selector) == 0:
        if allowMiss:
            return ""
        raise KeyError("Not found: " + str(selector))
    text = [x.strip() for x in selector.extract()]
    for t in text:
        if t:
            return t
    if not allowEmpty:
        raise KeyError("No text in " + str(selector))
    return ""