
def fun(name):
    path = f'static/temp/images/{name}.jpg'
    with open(path, 'w') as f:
        f.write('')
        return path