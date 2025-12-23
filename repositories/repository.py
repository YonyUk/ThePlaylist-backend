from typing import Any, TypeVar,Generic,Sequence,Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from abc import ABC,abstractmethod
from database import BaseModel

ModelType = TypeVar('ModelType',bound=BaseModel) # type: ignore

class Repository(Generic[ModelType],ABC):

    def __init__(self,model:type[ModelType],db:AsyncSession):
        '''
        Docstring for __init__
        
        :param model: entity model over which this repository will work
        :type model: type[ModelType]
        :param db: database session
        :type db: AsyncSession
        '''
        self._model = model
        self._db = db
    
    @abstractmethod
    async def _try_get_instance(self,instance:ModelType) -> ModelType | None:
        '''
        Docstring for _try_get_instance
        
        :param instance: instance to get
        :type instance: ModelType
        :return: try to get an instance by any of its unique field
        :rtype: ModelType | None
        '''
        raise NotImplementedError()
    
    def _instance_to_dict(self,instance:ModelType) -> Dict[str,Any]:
        '''
        Docstring for _instance_to_dict
        
        :param instance: entity instance
        :type instance: ModelType
        :return: a dictionary representing the instance
        :rtype: Dict[str, Any]
        '''
        return {
            key:getattr(instance,key)
            for key in instance.__mapper__.columns.keys()
            if hasattr(instance,key)
        }
    
    async def get_instances(self,limit:int=100,skip:int=0) -> Sequence[ModelType]:
        '''
        Docstring for get_instances
        
        :param limit: limit of results
        :type limit: int
        :param skip: number of registers to jump
        :type skip: int
        :rtype: Sequence[ModelType]
        '''
        query = select(self._model).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()
    
    async def get_by_id(self,instance_id:str) -> ModelType | None:
        '''
        Docstring for get_by_id
        
        :param id: id of the instances to retrieve
        :type id: str
        :return: the asked instance if exists or None
        :rtype: ModelType | None
        '''

        query = select(self._model).where(self._model.id==instance_id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self,instance:ModelType) -> ModelType | None:
        '''
        Docstring for create
        
        :param instance: instance to create
        :type instance: ModelType
        :return: the created instance if success, else None
        :rtype: ModelType | None
        '''
        try:
            async with self._db.begin():                
                db_instance = await self._try_get_instance(instance)
                if db_instance:
                    return None
                self._db.add(instance)
                await self._db.commit()
                await self._db.refresh(instance)
                return instance
        except Exception:
            await self._db.rollback()
            return None
    
    async def update(self,instance_id:str,update_instance:ModelType) -> ModelType | None:
        '''
        Docstring for update
        
        :param instance_id: id instance to update
        :type instance_id: str
        :param update_instance: new data for the update
        :type update_instance: ModelType
        :return: the instance with the data updated if success, else None
        :rtype: ModelType | None
        '''
        try:
            async with self._db.begin():
                db_instance = await self.get_by_id(instance_id)
                if not db_instance:
                    return None
                update_data = self._instance_to_dict(update_instance)
                await self._db.execute(
                    update(self._model).where(self._model.id==instance_id).values(**update_data)
                )
                await self._db.commit()
                await self._db.refresh(db_instance)

                return db_instance
        except Exception:
            await self._db.rollback()
            return None
    
    async def delete(self,instance_id:str) -> bool:
        '''
        Docstring for delete
        
        :param instance_id: id of the instance to delete
        :type instance_id: str
        :return: True if the instance was deleted successfully, False otherwise 
        :rtype: bool
        '''
        try:
            async with self._db.begin():
                db_instance = await self.get_by_id(instance_id)
                if not db_instance:
                    return False
                await self._db.delete(db_instance)
                await self._db.commit()
                return True
        except Exception:
            await self._db.rollback()
            return False