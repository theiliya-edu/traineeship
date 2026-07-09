from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spimex_parser.config import settings

engine = create_engine(settings.db.url, echo=False)
Session = sessionmaker(engine)
