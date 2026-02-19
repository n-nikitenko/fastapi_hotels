from .hotels import router as hotels_router
from .rooms import router as rooms_router
from .auth import router as auth_router

__all__=["hotels_router", "rooms_router"]