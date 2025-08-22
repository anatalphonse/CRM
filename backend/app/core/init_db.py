from app.core.database import engine
from app.models import user

print("Creating table")
user.Base.metadata.create_all(bind=engine)
print("Table created succesfully")