# -*- coding: utf-8 -*-

from pydantic import BaseModel

class Representation(BaseModel):
    name: str | None
