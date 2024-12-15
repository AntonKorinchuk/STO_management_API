import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import user routes
from crud.user import router as user_router
from crud.appointment import router as appointment_router
from crud.services import router as service_router
from crud.mechanic import router as mechanic_router
from crud.document import router as document_router
from crud.car import router as car_router

app = FastAPI(
    title="Car Service API",
    description="API for car service management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких джерел
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі HTTP-методи
    allow_headers=["*"],  # Дозволяє всі заголовки
)

# Include routers
app.include_router(user_router, prefix="/api/v1")
app.include_router(appointment_router, prefix="/api/v1")
app.include_router(service_router, prefix="/api/v1")
app.include_router(mechanic_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")
app.include_router(car_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to Car Service API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
