from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    id : str 
    lawbook : Optional[str]
    levelId : Optional[str]
    paragraphEid : Optional[str]
    paragraphText : Optional[str]
    footnoteText : Optional[str]
    articleNum : Optional[int]
    articleNumMinor : Optional[str]
    paragraphNum : Optional[int]
    paragraphNumMinor : Optional[str]