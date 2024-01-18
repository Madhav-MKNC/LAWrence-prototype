from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Article

router = APIRouter()

@router.get("/test", response_description="writes an arbitrary element out", response_model=List[Article])
async def test(request: Request):
    articles = [article async for article in request.app.lawbook_container.query_items(
        query='SELECT * FROM SwissLawbook r WHERE r.bookName="OR" AND r.articleNum=13 AND r.paragraphNum=1')]
    return articles


@router.post("/getParagraph", response_description="Will return the detailed paragraph text for a given paragraph number.", response_model=List[Article])
async def getParagraph(request: Request, bookName: str, articleNum: int, articleNumMinor: str = None, paragraphNum: int = None):
    query = "SELECT * FROM SwissLawbook r WHERE r.bookName=@bookName AND r.articleNum=@articleNum"
    parameters = [
        {"name": "@bookName", "value": bookName},
        {"name": "@articleNum", "value": articleNum}
    ]
    articles = [article async for article in request.app.lawbook_container.query_items(query=query, parameters=parameters)]
        
    return articles


@router.get("/getParagraphs", response_description="Will return the detailed paragraph text for a given paragraph number. If paragraph is not provided, a list of paragraphs in this article are returned.", response_model=List[Article])
async def getParagraphs(request: Request, bookName: str, articleNum: int, articleNumMinor: str = None, paragraphNum: int = None):
    query = "SELECT * FROM SwissLawbook r WHERE r.bookName=@bookName AND r.articleNum=@articleNum"
    parameters = [
        {"name": "@bookName", "value": bookName},
        {"name": "@articleNum", "value": articleNum}
    ]

    if articleNumMinor is not None:
        query += " AND r.articleNumMinor=@articleNumMinor"
        parameters.append({"name": "@articleNumMinor", "value": articleNumMinor})

    if paragraphNum is not None:
        query += " AND r.paragraphNum=@paragraphNum"
        parameters.append({"name": "@paragraphNum", "value": paragraphNum})

    articles = [article async for article in request.app.lawbook_container.query_items(query=query, parameters=parameters)]
    return articles
     