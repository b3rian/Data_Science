def add_items(item, items = None):
    if items is None:
        items = []
    items.append(item)
    return items

x = add_items(10)
print(x)
 