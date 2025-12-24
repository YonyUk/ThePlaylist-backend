from typing import Sequence,Generic,TypeVar
from pydantic import BaseModel as SchemaBaseModel
from uuid import uuid4
from database import BaseModel as DataBaseModel
from repositories.repository import Repository

ModelType = TypeVar('ModelType',bound=DataBaseModel) # type: ignore
RepositoryType = TypeVar('RepositoryType',bound=Repository)
CreateSchemaType = TypeVar('CreateSchemaType',bound=SchemaBaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType',bound=SchemaBaseModel)
SchemaType = TypeVar('SchemaType',bound=SchemaBaseModel)

class Service(Generic[
    ModelType,
    RepositoryType,
    CreateSchemaType,
    UpdateSchemaType,
    SchemaType
]):
    
    def __init__(
        self,
        model:type[ModelType],
        schema:type[SchemaType],
        repository:RepositoryType,
        exclude_fields:set=set(),
        exclude_unset:bool=True
    ):
        '''
        Docstring for __init__
        
        :type model: type[ModelType]
        :param repository: repository over which this service will work
        :type repository: RepositoryType
        :param exclude_fields: fields to exclude from schemas internally when calling function
        '_get_instance' through method 'Schema.model_dump'
        :type exclude_fields: set
        :param exclude_unset: indicates what to do with fields unset in 'Schema.model_dump'
        :type exclude_unset: bool
        '''

        self._model = model
        self._schema = schema
        self._repository = repository
        self._exclude_fields = exclude_fields
        self._exclude_unset = exclude_unset or len(exclude_fields) > 0
    
    async def _to_schema(self,model:ModelType | None) -> SchemaType | None:
        '''
        Docstring for _to_schema
        
        :param model: instance to convert to schema
        :type model: ModelType | None
        :return: the schema for this instance
        :rtype: SchemaType | None
        '''
        if not model:
            return None
        return self._schema.model_validate(model)
    
    async def _get_instance(self,**fields) -> ModelType:
        '''
        Docstring for _get_instance
        
        :return: the instance for the given values
        :rtype: ModelType
        '''
        return self._model(**fields)
    
    async def get_by_id(self,id:str) -> SchemaType | None:
        '''
        Docstring for get_by_id
        
        :type id: str
        :return: the asked object
        :rtype: SchemaType | None
        '''
        model = await self._repository.get_by_id(id)
        return await self._to_schema(model)

    async def get(self,limit:int=100,skip:int=0) -> Sequence[SchemaType]:
        '''
        Docstring for get
        
        :param limit: limit of results
        :type limit: int
        :param skip: number of registers to skip
        :type skip: int
        :rtype: Sequence[SchemaType]
        '''

        results = await self._repository.get_instances(limit,skip)
        instances = []
        for instance in results:
            ins = await self._to_schema(instance)
            instances.append(ins)
        return instances
    
    async def create(self,value:CreateSchemaType,**extra_fields) -> SchemaType | None:
        '''
        Docstring for create
        
        :type value: CreateSchemaType
        :param extra_fields: extra fields for model creation
        :rtype: SchemaType | None
        '''

        db_instance = await self._get_instance(
            **{
                **value.model_dump(
                    exclude=self._exclude_fields,
                    exclude_unset=self._exclude_unset
                ),
                **extra_fields,
                **{
                    'id':str(uuid4())
                }
            }
        )
        db_instance = await self._repository.create(db_instance)
        if not db_instance:
            return None
        return await self._to_schema(db_instance)
    
    async def update(self,id:str,update_data:UpdateSchemaType,**extra_fields) -> SchemaType | None:
        '''
        Docstring for update
        
        :type id: str
        :param update_data: new data
        :type update_data: UpdateSchemaType
        :param extra_fields: extra fields to update
        :rtype: SchemaType | None
        '''

        db_instance = await self._repository.get_by_id(id)
        if not db_instance:
            return None
        update_instance = await self._get_instance(**{
            **update_data.model_dump(
                exclude=self._exclude_fields,
                exclude_unset=self._exclude_unset
            ),
            **extra_fields,
            **{
                'id':id
            }
        })
        return await self._repository.update(id,update_instance)
    
    async def delete(self,id:str) -> bool:
        '''
        Docstring for delete
        
        :type id: str
        :rtype: bool
        '''
        return await self._repository.delete(id)