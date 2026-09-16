from enum import unique
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.repository import Repository



class GitHubProfile(Base):
     #name of the tabe in POSTgREs
     __tablename__ = "github_profiles"

     #primary key ID (auto incremtn integer)
     id: Mapped[int] =  mapped_column(primary_key = True, index =True)

     #unique github username (e.g -boka ), indexed for fast search
     username: Mapped[str] =  mapped_column(String(255),  unique = True, index = True, nullable = False)
    
    #one to many RELAtion ship : One profile has many relationsship 
     repositories: Mapped[List["Repository"]] = relationship( "Repository" , back_populates= "profile", 
                                                  cascade= "all, delete-orphan" )