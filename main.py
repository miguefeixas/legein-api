from fastapi import FastAPI

from src.routers.auth import auth
from src.routers.author import author
from src.routers.book import book
from src.routers.genre import genre
from src.routers.health import health
from src.routers.user import user
from src.routers.review import review
from src.routers.publisher import publisher
from src.routers.friendship import friendship
from src.routers.notification import notification
from src.routers.book_list import book_list
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path='/api')

origins = [
    'http://localhost:4200',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(author.router)
app.include_router(book.router)
app.include_router(genre.router)
app.include_router(review.router)
app.include_router(publisher.router)
app.include_router(friendship.router)
app.include_router(notification.router)
app.include_router(book_list.router)
