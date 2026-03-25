def build_context_from_record(record):
    return f"""
Name: {record.name}
Email: {record.email}
Phone: {record.phone}
City: {record.city}
Organization: {record.organization}
DOB: {record.dob}
""".strip()