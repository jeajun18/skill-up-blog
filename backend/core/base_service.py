from typing import TypeVar, Generic

from django.db.models import Model, QuerySet


T = TypeVar('T', bound=Model)


class BaseService(Generic[T]):
    model: T

    def get_queryset(self) -> QuerySet[T]:
        return self.model.objects.all()
    
    def get(self, **kwargs) -> T | None:
        return self.get_queryset().filter(**kwargs).first()
    
    def filter(self, **kwargs) -> QuerySet[T]:
        return self.get_queryset().filter(**kwargs)
    
    def create(self, **kwargs) -> T:
        return self.model.objects.create(**kwargs)
    
    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: T) -> None:
        instance.delete() 