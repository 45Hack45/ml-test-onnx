from sqlmodel import Field, SQLModel


class ModelBase(SQLModel):
    id: int = Field(primary_key=True, nullable=False, index=True)
