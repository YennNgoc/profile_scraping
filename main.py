from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse
from utils.linkedin import LinkedinScraper
from utils.careerviet import CareervietScraper
import os
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/linkedin")
def read_item(title:  Union[str, None] = '', location: Union[str, None] = 'viet nam', orther: Union[str, None] = ''):
    LinkedinScraper.run(title, location, orther)

@app.get("/careerviet")
def read_item(category:  Union[str, None] = '', page: int = 1):
    CareervietScraper.run(category, page)

@app.get("/download/{souce_name}/{profile_id}")
async def download_file(souce_name: str, profile_id):
    backend_location = os.path.join('utils', souce_name, 'CVs' , profile_id+'.pdf')
    print(backend_location)

    # Check if the file exists
    if os.path.exists(backend_location):
        return FileResponse(backend_location, filename=profile_id+'.pdf')
    else:
        return {"error": "File not found"}