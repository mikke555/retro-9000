from pydantic import BaseModel


class Submission(BaseModel):
    id: str
    name: str
