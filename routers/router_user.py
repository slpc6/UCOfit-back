# Router para la gestion de usuarios de la aplicacion UCOfit

# External libraries
from fastapi import APIRouter


router = APIRouter(prefix='/user',
                        tags=['User'])


@router.post('/register')
def register():
    return {'msg': 'register'}


@router.delete('/delete')
def delete():
    return {'msg': 'delete'}


@router.post('/login')
def login():
    return {'msg': 'login'}


@router.post('/logout')
def logout():
    return {'msg': 'logout'}
