from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    url: str

# 👇 ADD THIS LINE
AnalyzeRequest.model_rebuild()