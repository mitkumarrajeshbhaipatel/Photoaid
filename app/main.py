from fastapi import FastAPI
from app.routers import auth, profile, admin, location, matchmaking, session, chat, notification, review, media

app = FastAPI()

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(admin.router) 
app.include_router(location.router)
app.include_router(matchmaking.router)
app.include_router(session.router)
app.include_router(chat.router)  
app.include_router(notification.router)
app.include_router(review.router)
app.include_router(media.router)