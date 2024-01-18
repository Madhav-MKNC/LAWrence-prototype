# Utilites / helper function

import os 
from dotenv import load_dotenv
load_dotenv()

from data_models import *
import json

from openai import OpenAI, OpenAIError
from azure.cosmos import CosmosClient
from azure.cosmos import CosmosClient, PartitionKey, exceptions

from prompts import SUMMARY_PROMPT, ARTICLES_PROMPT


# Openai setup
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'],)
GPT_MODEL = "gpt-4-1106-preview"

# Azure Cosmos DB setup
ENDPOINT = os.environ['ENDPOINT']
COSMOS_DB_KEY = os.environ['COSMOS_DB_KEY']
DATABASE_NAME = os.environ['DATABASE_NAME']
CONTAINER_NAME = os.environ['CONTAINER_NAME']

# connect to cosmos db
cosmos_client = CosmosClient(ENDPOINT, COSMOS_DB_KEY)
database = cosmos_client.get_database_client(DATABASE_NAME)
cosmos_container = database.get_container_client(CONTAINER_NAME)


# openai API call
def get_gpt_response(
    prompt_content: str,
    role: str = 'user',
    model: str = GPT_MODEL,
    response_format: str = "text"
) -> str:
    """
    This functions is for OpenAI API calls
    """
    
    prompt = [
        {
            'role': role,
            'content': prompt_content
        }
    ]

    try:
        response = openai_client.chat.completions.create(
            messages = prompt,
            model = model,
            response_format = {"type": response_format}
        )
        output = response.choices[0].message.content
        return output
    
    except OpenAIError as e:
        print('\033[31m*** get_gpt_response():', str(e), "\033[m")


# Validating if GPT returned articles in expected format
def validate_articles(output: str) -> List[GPTArticle]:
    """
    Expects the output:str returned from openai API call in the following structure:-
    {
        'some key': [
            {
                "article_ref": "CO ART. 337",
                "article_book": "CO",
                "article_num": 337,
                "article_num_minor": null,
                "paragraph_num": null,
                "paragraph_num_minor": null
            }
        ]
    }
    """
    articles = []
    try:
        output = json.loads(output)
        output = list(output.values())[0]
        print("\033[93m[+] Articles retured from GPT:")
        print(str(output) + "\033[m")
        for article in output:
            articles.append(GPTArticle(**article))
        print('[+] Validated articles returned from GPT.')
    except Exception as e:
        print('\033[31m*** validate_articles():', str(e), "\033[m")
    return articles


# Summarize legal situation
def get_summary(user_request: UserRequest.Summary) -> Response.Summary:
    """
    Returns a summary in a bullet point list for the given legal text.
    """
    
    legal_situation = user_request.legal_situation
    language = user_request.language

    prompt_content = SUMMARY_PROMPT.format(
        language = language,
        situation = legal_situation
    )
    #######################################
    ## TODO: prompt v/s str manipulation ##
    #######################################
    summary = get_gpt_response(prompt_content=prompt_content, role="system")
    summary_response = Response.Summary(
        title = "summary",
        summary_enum = [
            {
                "number" : 1,
                "content" : summary
            }
        ]
    )
    return summary_response


# Get articles based on the legal situation and questions
def get_articles(user_request: UserRequest.Articles) -> Response.Articles:
    """
    Used by the UI to retrieve the articles that fit the legal questions.
    """

    legal_questions_responses = []
    for question in user_request.legal_questions:
        articles = find_relevant_articles(
            situation = user_request.legal_situation,
            question = question.question,
            language = user_request.language
        )
        legal_questions_response = QuestionResponse(
            question_ref = question.number,
            articles = articles
        )
        legal_questions_responses.append(legal_questions_response)

    user_response = Response.Articles(
        request_id = user_request.request_id,
        user_id = user_request.user_id,
        language = user_request.language,
        status = 'Open', # defeault to 'Open'
        legal_questions = legal_questions_responses
    )
    return user_response


# Get paragraph text from cosmos DB
def fetch_paragraphs(user_request: UserRequest.Paragraphs) -> List[Paragraph]:
    """
    Will return the articles with detailed paragraph text for a given paragraph number.
    If paragraph is not provided, a list of paragraphs in this article are returned."
    """
    
    bookName = user_request.bookName
    articleNum = user_request.articleNum
    articleNumMinor = user_request.articleNumMinor
    paragraphNum = user_request.paragraphNum

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

    try:
        items = list(cosmos_container.query_items(
            query = query,
            parameters = parameters,
            enable_cross_partition_query = True
        ))
        paragraphs = [Paragraph(**item) for item in items]

    except Exception as e:
        paragraphs = []
        print('\033[31m*** fetch_paragraphs():', str(e), "\033[m")
        
    return paragraphs


# Retrieve articles with GPT
def find_relevant_articles(
        situation: str,
        question: str,
        language: str
) -> List[Article]:
    """
    This function calls the LLM to retrieve the relevant articles for the legal situation and each legal question.
    """

    prompt_content = ARTICLES_PROMPT.format(
        situation = situation,
        question = question,
        language = language
    )
    response = get_gpt_response(prompt_content=prompt_content, role="system", response_format = "json_object")
    gpt_articles = validate_articles(response)

    # Fetching paragraphs from cosmos db
    articles = []
    for gpt_article in gpt_articles:
        paragraphs = fetch_paragraphs(
            # getParagraphs API call
            user_request = UserRequest.Paragraphs(
                bookName = gpt_article.article_book,
                articleNum = gpt_article.article_num,
                articleNumMinor = gpt_article.article_num_minor,
                paragraphNum = gpt_article.paragraph_num
            )
        )
        article = Article(
            # id = ...,
            # level_id = ...,
            lawbook = gpt_article.article_book,
            articleRef = gpt_article.article_ref,
            articleNum = gpt_article.article_num,
            articleNumMinor = gpt_article.article_num_minor,
            paragraphs = paragraphs
        )

        articles.append(article)

    # Remove duplicates
    final_articles = []
    for article in articles:
        if article not in final_articles:
            final_articles.append(article)

    return final_articles
