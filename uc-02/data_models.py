# Data models for parsing and validating data

from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Dict, Any


class Paragraph(BaseModel):
    """
    Paragraph data model.
    """
    id : Optional[str]  = Field(default=None)
    levelId : Optional[str] = Field(default=None)
    bookName: str
    articleNum : int
    articleNumMinor : Optional[str] = Field(default=None)
    paragraphNum : int
    paragraphNumMinor : Optional[str] = Field(default=None)
    paragraphText : Optional[str] = Field(default=None)
    paragraphEid : Optional[str] = Field(default=None)

class Article(BaseModel):
    """
    Article data model.
    """
    id: Optional[str] = Field(default=None)         # Different for each paragraphs[i]
    level_id: Optional[str] = Field(default=None)   # Different for each paragraphs[i]
    lawbook : str
    articleRef: str
    articleNum: int
    articleNumMinor: Optional[str] = Field(default=None)
    paragraphs: List[Paragraph]

class GPTArticle(BaseModel):
    """
    Structure in which GPT must return articles (prompt).
    """
    article_ref: str
    article_book: str
    article_num: int
    article_num_minor: Optional[str]
    paragraph_num: Optional[int]

class Question(BaseModel):
    number: int
    question: str

class QuestionResponse(BaseModel):
    question_ref: Optional[int]
    articles: List[Article]

class UserRequest(BaseModel):
    """
    For handling and validating user requests.
    """

    class Summary(BaseModel):
        user_id: Optional[int]
        language: Optional[str]
        legal_situation: str

    class Articles(BaseModel):
        user_id: Optional[int]
        request_id: Optional[int]
        language: Optional[str]
        legal_situation: str
        legal_questions: List[Question]

    class Paragraphs(BaseModel):
        bookName: str
        articleNum: int
        articleNumMinor: Optional[str]
        paragraphNum: Optional[int]


class Response(BaseModel):
    """
    Server reponses to API endpoints.
    """

    class Summary(BaseModel):
        title: str
        summary_enum: List[Dict[str, Any]]

    class Articles(BaseModel):
        request_id: Optional[int]
        user_id: Optional[int]
        language: Optional[str]
        status: str
        legal_questions: List[QuestionResponse]
