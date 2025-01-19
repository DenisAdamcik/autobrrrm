from app import db_manager
from app.models import Base

# Bind the Base to the engine
Base.metadata.bind = db_manager.engine

# Create all tables
Base.metadata.create_all(db_manager.engine)