def extract(selector):
    text = [x.strip() for x in selector.extract()]
    for t in text:
        if t:
            return t