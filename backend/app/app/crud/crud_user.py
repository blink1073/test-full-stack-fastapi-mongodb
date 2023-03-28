from typing import Any, Dict, Optional, Union

from pymongo.database import Database

from app.core.security import get_password_hash, verify_password, create_new_totp
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, UserUpdate
from app.schemas.totp import NewTOTP


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Database, *, email: str) -> Optional[User]:
        model = db.users.find_one({'email': email})
        if model:
            return User(**model)

    def create(self, db: Database, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        if obj_in.password:
            db_obj.hashed_password = get_password_hash(obj_in.password)
        db.users.insert_one(db_obj.dict())
        return db_obj

    def update(self, db: Database, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        import pdb; pdb.set_trace()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("email") and db_obj.email != update_data["email"]:
            update_data["email_validated"] = False
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Database, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(plain_password=password, hashed_password=user.hashed_password):
            return None
        return user

    def validate_email(self, db: Database, *, db_obj: User) -> User:
        obj_in = UserUpdate(**UserInDB.from_orm(db_obj).dict())
        obj_in.email_validated = True
        return self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def activate_totp(self, db: Database, *, db_obj: User, totp_in: NewTOTP) -> User:
        obj_in = UserUpdate(**UserInDB.from_orm(db_obj).dict())
        obj_in = obj_in.dict(exclude_unset=True)
        obj_in["totp_secret"] = totp_in.secret
        return self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def deactivate_totp(self, db: Database, *, db_obj: User) -> User:
        obj_in = UserUpdate(**UserInDB.from_orm(db_obj).dict())
        obj_in = obj_in.dict(exclude_unset=True)
        obj_in["totp_secret"] = None
        obj_in["totp_counter"] = None
        return self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def update_totp_counter(self, db: Database, *, db_obj: User, new_counter: int) -> User:
        obj_in = UserUpdate(**UserInDB.from_orm(db_obj).dict())
        obj_in = obj_in.dict(exclude_unset=True)
        obj_in["totp_counter"] = new_counter
        return self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def toggle_user_state(self, db: Database, *, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        db_obj = self.get_by_email(db, email=obj_in.email)
        if not db_obj:
            return None
        return self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def is_email_validated(self, user: User) -> bool:
        return user.email_validated


user = CRUDUser(User)
