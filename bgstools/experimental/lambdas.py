# lambda function to upsert data into a dictionary
upsert_data = lambda data, key, value: {**data, **{key: value}} if key not in data else data
