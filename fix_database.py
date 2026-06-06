content = open("app/database.py").read()

# Remove the bare create_index call
content = content.replace(
    'otp_collection.create_index("created_at", expireAfterSeconds=600)',
    '''
def ensure_indexes():
    try:
        otp_collection.create_index("created_at", expireAfterSeconds=600)
        print("MongoDB indexes created")
    except Exception as e:
        print(f"Index creation warning: {e}")
'''
)

with open("app/database.py", "w", encoding="utf-8") as f:
    f.write(content)
print("database.py fixed")