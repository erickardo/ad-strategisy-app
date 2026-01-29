from pydantic import BaseModel
from typing import List

class AdVariation(BaseModel):
    title: str
    body: str
    type: str

class AdOutput(BaseModel):
    ad_variations: List[AdVariation]
    creative_concepts: List[str]