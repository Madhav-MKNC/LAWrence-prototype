
# start with uvicorn main:app --reload
# check the swagger API on http://127.0.0.1:8000/docs (or redocs)


from fastapi import FastAPI
from dotenv import dotenv_values
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, exceptions
from routes import router as lawbook_router

config = dotenv_values(".env")
app = FastAPI()
DATABASE_NAME = "Lawbook"
CONTAINER_NAME = "SwissLawbook"

app.include_router(lawbook_router, tags=['lawbook'], prefix='/lawbook')

@app.on_event("startup")
async def startup_db_client():
     app.cosmos_client = CosmosClient(config["CosmosDBuri"], credential = config["CosmosDBkey"])
     await get_or_create_db(DATABASE_NAME)
     await get_or_create_container(CONTAINER_NAME)
     
async def get_or_create_db(db_name):
    try:
        app.database  = app.cosmos_client.get_database_client(db_name)
        return await app.database.read()
    except exceptions.CosmosResourceNotFoundError:
        print("Creating database")
        return await app.cosmos_client.create_database(db_name)
     
async def get_or_create_container(container_name):
    try:        
        app.lawbook_container = app.database.get_container_client(container_name)
        return await app.lawbook_container.read()   
    except exceptions.CosmosResourceNotFoundError:
        print("Creating container with id as partition key")
        return await app.database.create_container(id=container_name, partition_key=PartitionKey(path="/id"))
    except exceptions.CosmosHttpResponseError:
        raise