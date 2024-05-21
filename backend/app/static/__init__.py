import os
from starlette.routing import Router
from fastapi.staticfiles import StaticFiles

router = Router()

print(os.path.join(os.path.dirname(__file__), "../../static"))

router.mount(
    "/",
    StaticFiles(
        directory=os.path.join(os.path.dirname(__file__), "../../static"), html=True
    ),
    name="static",
)
