import hashlib,json
def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def measurement_record(row):
    return {"source_key":row.source_key,"sequence":row.sequence,"measured_at":row.measured_at,"value":row.value}
