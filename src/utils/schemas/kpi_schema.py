from black import List
from pydantic import BaseModel, create_model
from typing import Type


def create_kpi_schema(base_schema: Type[BaseModel]) -> Type[BaseModel]:
    """
    Create a schema for the KPIs using a dynamic schema
    """
    return create_model('KpiSchema', total_past_week=(int, ...), this_week=(List[base_schema], ...))
