from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pymongo.database import Database

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A Pydantic model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Database, id: Any) -> Optional[ModelType]:
        col = db[self.model.__name__.lower() + 's']
        model = col.find_one({'id': id})
        return self.model(**model)

    def get_multi(
        self, db: Database, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        col = db[self.model.__name__.lower() + 's']
        return list(col.find({}, skip=skip, limit=limit))

    def create(self, db: Database, *, obj_in: CreateSchemaType) -> ModelType:
        import pdb; pdb.set_trace()
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Database,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        col = db[self.model.__name__.lower() + 's']
        col.insert_one(db_obj.dict())
        return db_obj

    def remove(self, db: Database, *, id: int) -> ModelType:
        import pdb; pdb.set_trace()
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
