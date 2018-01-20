import gc
for obj in gc.get_objects():
    if isinstance(obj, datasource):
        obj.save_results()

