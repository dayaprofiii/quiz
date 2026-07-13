from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import SessionLocal, create_db_schema
from app.services.rooms import room_manager
from app.services.seed import seed_demo_data


settings = get_settings()


FIELD_NAMES = {
    'email': 'электронная почта',
    'password': 'пароль',
    'name': 'имя пользователя',
    'title': 'название',
    'ownerId': 'пользователь',
    'quizId': 'викторина',
    'organizerId': 'организатор',
    'userId': 'участник',
    'answerIds': 'ответ',
    'questions': 'вопросы',
    'answers': 'ответы',
    'timeLimit': 'время на ответ',
    'currentPassword': 'текущий пароль',
    'nextPassword': 'новый пароль',
}


def validation_message(error: dict) -> str:
    location = [part for part in error.get('loc', []) if part != 'body']
    field = next((part for part in reversed(location) if isinstance(part, str)), '')
    field_name = FIELD_NAMES.get(field, field or 'поле')
    error_type = str(error.get('type', ''))
    context = error.get('ctx') or {}

    if error_type == 'json_invalid':
        return 'Некорректный формат запроса. Проверьте введённые данные.'
    if error_type == 'missing':
        return f'Заполните поле «{field_name}».'
    if error_type == 'string_too_short':
        min_length = context.get('min_length')
        if min_length and int(min_length) > 1:
            return f'Поле «{field_name}» должно содержать не меньше {min_length} символов.'
        return f'Заполните поле «{field_name}».'
    if error_type == 'string_too_long':
        return f'Поле «{field_name}» слишком длинное.'
    if error_type in {'int_parsing', 'int_type', 'float_parsing', 'float_type'}:
        return f'Поле «{field_name}» должно быть числом.'
    if error_type == 'greater_than_equal':
        return f'Поле «{field_name}» должно быть не меньше {context.get("ge")}.'
    if error_type in {'list_type', 'model_attributes_type', 'dict_type'}:
        return 'Некорректный формат данных. Проверьте заполненные поля.'
    if error_type == 'literal_error':
        return f'В поле «{field_name}» выбрано недопустимое значение.'

    message = str(error.get('msg') or '').replace('Value error, ', '')
    if message and not message.lower().startswith(('field required', 'input should')):
        return message
    return 'Проверьте заполненные поля и попробуйте снова.'


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_db:
        await create_db_schema()
    if settings.seed_demo_data:
        async with SessionLocal() as session:
            await seed_demo_data(session)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    return JSONResponse(status_code=422, content={'message': validation_message(first_error)})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'message': exc.detail})


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={'message': 'Данные конфликтуют с уже существующей записью.'})


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'message': 'Внутренняя ошибка сервера. Попробуйте позже.'})


@app.get('/health', include_in_schema=False)
async def health():
    return {'status': 'ok'}


@app.websocket('/')
async def room_websocket(websocket: WebSocket):
    code = websocket.query_params.get('code')
    try:
        room = await room_manager.connect(websocket, code or '')
    except HTTPException as exc:
        await websocket.accept()
        await websocket.send_json({'type': 'error', 'message': exc.detail})
        await websocket.close(code=1008)
        return
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        room_manager.disconnect(room, websocket)
