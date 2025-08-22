from fastapi import FastAPI
from app.api.v1 import routes, admin_users, contact_routes, lead_routes, task_routes, auth_routes

app = FastAPI(title="CRM_backend")

# include routes


@app.get("/")
async def root():
    return {"message": "CRM backend is running"}

app.include_router(routes.router)
app.include_router(admin_users.router)
app.include_router(auth_routes.router)
app.include_router(contact_routes.router)
app.include_router(lead_routes.router)
app.include_router(task_routes.router)
