import json
import logging
import os
import traceback
from datetime import timedelta
from json import JSONDecodeError
from functools import wraps

import requests
from fastapi import FastAPI, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from llmx import providers
from sqlalchemy import delete
from sqlalchemy.orm import Session

from lida.ext.ollama.local import LocalTextGenerator
from lida.ext.auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_user, \
    get_current_user
from lida.ext.entity import SessionLocal, Chat, Goal, Explain, Evaluate, Edit, User
from ..components import Manager
from ..datamodel import GoalWebRequest, SummaryUrlRequest, TextGenerationConfig, VisualizeEditWebRequest, \
    VisualizeEvalWebRequest, VisualizeExplainWebRequest, VisualizeRecommendRequest, VisualizeRepairWebRequest, \
    VisualizeWebRequest, InfographicsRequest, VisualizeConclusionRequest, DescribeData, UserCreate, VisWebRequest

# 设置环境变量
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/"
os.environ["OPENAI_API_KEY"] = "EMPTY"

textgen = LocalTextGenerator(
    provider="ollama",
    api_key="EMPTY",
    model="deepseek-r1",
    # api_version="v1",
    api_base="http://localhost:11434"
)

logger = logging.getLogger("lida")
api_docs = os.environ.get("LIDA_API_DOCS", "False") == "True"

lida = Manager(text_gen=textgen)
app = FastAPI()
# allow cross origin requests for testing on localhost:800* ports only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api = FastAPI(root_path="/api", docs_url="/docs" if api_docs else None, redoc_url=None)
app.mount("/api", api)

root_file_path = os.path.dirname(os.path.abspath(__file__))
static_folder_root = os.path.join(root_file_path, "ui")
files_static_root = os.path.join(root_file_path, "files/")
data_folder = os.path.join(root_file_path, "files/data")
os.makedirs(data_folder, exist_ok=True)
os.makedirs(files_static_root, exist_ok=True)
os.makedirs(static_folder_root, exist_ok=True)

# mount lida front end UI files
app.mount("/", StaticFiles(directory=static_folder_root, html=True), name="ui")
api.mount("/files", StaticFiles(directory=files_static_root, html=True), name="files")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def check_model


def handle_api_exceptions(func):
    """装饰器：捕获 API 接口异常，打印堆栈和请求参数"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # 提取请求参数
            request_params = {}
            for key, value in kwargs.items():
                if hasattr(value, 'dict') and callable(getattr(value, 'dict')):
                    # Pydantic 模型转为字典
                    try:
                        request_params[key] = value.dict()
                    except Exception:
                        request_params[key] = str(value)
                elif hasattr(value, '__dict__'):
                    # 其他对象转为字典
                    request_params[key] = value.__dict__
                else:
                    # 基本类型直接保存
                    request_params[key] = value

            return await func(*args, **kwargs)
        except Exception as exception_error:
            # 打印完整的错误信息
            error_message = f"""\n{'=' * 80}
【API 接口异常】{func.__name__}
{'=' * 80}
【请求参数】
{json.dumps(request_params, indent=2, default=str, ensure_ascii=False)}
【异常信息】
{type(exception_error).__name__}: {str(exception_error)}
【堆栈跟踪】
{traceback.format_exc()}
{'=' * 80}"""
            logger.error(error_message)
            print(error_message)  # 同时输出到控制台

            # 返回错误响应
            return {
                "status": False,
                "message": f"Error in {func.__name__}: {str(exception_error)}"
            }

    return wrapper


def handle_sync_api_exceptions(func):
    """装饰器：捕获同步 API 接口异常，打印堆栈和请求参数"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 提取请求参数
            request_params = {}
            for key, value in kwargs.items():
                if hasattr(value, 'dict') and callable(getattr(value, 'dict')):
                    # Pydantic 模型转为字典
                    try:
                        request_params[key] = value.dict()
                    except Exception:
                        request_params[key] = str(value)
                elif hasattr(value, '__dict__'):
                    # 其他对象转为字典
                    request_params[key] = value.__dict__
                else:
                    # 基本类型直接保存
                    request_params[key] = value

            return func(*args, **kwargs)
        except Exception as exception_error:
            # 打印完整的错误信息
            error_message = f"""\n{'=' * 80}
【API 接口异常】{func.__name__}
{'=' * 80}
【请求参数】
{json.dumps(request_params, indent=2, default=str, ensure_ascii=False)}
【异常信息】
{type(exception_error).__name__}: {str(exception_error)}
【堆栈跟踪】
{traceback.format_exc()}
{'=' * 80}"""
            logger.error(error_message)
            print(error_message)  # 同时输出到控制台

            # 返回错误响应
            return {
                "status": False,
                "message": f"Error in {func.__name__}: {str(exception_error)}"
            }

    return wrapper


# FastAPI 全局异常处理器，用于捕获 422 等 HTTP 异常
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """处理请求参数验证错误 (422)"""
    # 尝试获取请求体
    body = None
    try:
        import asyncio
        # 注意：这里无法直接获取原始请求体，因为已经被 FastAPI 解析过了
        # 但我们可以通过 exc.errors 看到验证错误详情
        error_details = exc.errors()
    except Exception:
        error_details = []

    error_message = f"""\n{'=' * 80}
【422 参数验证错误】{request.method} {request.url.path}
{'=' * 80}
【验证错误详情】
{json.dumps(error_details, indent=2, ensure_ascii=False)}
【异常信息】
{type(exc).__name__}: {str(exc)}
{'=' * 80}"""
    logger.error(error_message)
    print(error_message)

    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": f"参数验证失败：{str(exc)}",
            "errors": error_details
        }
    )


@api.post("/visualize")
@handle_api_exceptions
async def visualize_data(req: VisualizeWebRequest,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)) -> dict:
    """Generate goals given a dataset summary"""
    db_chat = db.query(Chat).filter(Chat.id == req.chat_id, Chat.user_id == current_user.id).first()
    if db_chat is None:
        return {"status": False,
                "message": "Chat not found with the given chat_id"}
    # print(req.textgen_config)
    charts = lida.visualize(
        summary=req.summary,
        goal=req.goal,
        textgen_config=req.textgen_config if req.textgen_config else TextGenerationConfig(),
        library=req.library, return_error=True)
    print("found charts: ", len(charts), " for goal: ")
    if len(charts) == 0:
        return {"status": False, "message": "No charts generated"}

    # save to database
    db_goal = db.query(Goal).filter(Goal.chat_id == req.chat_id, Goal.question == req.goal.question).first()
    if db_goal is None:
        db_goal = Goal(chat_id=req.chat_id,
                       index=req.goal.index,
                       question=req.goal.question,
                       visualization=req.goal.visualization,
                       rationale=req.goal.rationale,
                       is_auto=0,
                       library=req.library,
                       code=charts["code"])
    else:
        db_goal.library = req.library
        db_goal.code = charts[0].code
    db.commit()
    db.refresh(db_goal)

    return {"status": True, "charts": charts,
            "message": "Successfully generated charts.",
            "goal_id": db_goal.id}


@api.post("/visualize/edit")
@handle_api_exceptions
async def edit_visualization(req: VisualizeEditWebRequest,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)) -> dict:
    """Given a visualization code, and a goal, generate a new visualization"""
    db_goal = db.query(Goal).filter(Goal.chat_id == req.chat_id, Goal.id == req.goal_id).first()
    if db_goal is None:
        return {"status": False,
                "message": "Goal not found with the given chat_id and question"}

    textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig()
    charts = lida.edit(
        code=req.code,
        summary=req.summary,
        instructions=req.instructions,
        textgen_config=textgen_config,
        library=req.library, return_error=True)

    # charts = [asdict(chart) for chart in charts]
    if len(charts) == 0:
        return {"status": False, "message": "No charts generated"}

    # save to database
    db_goal.library = req.library
    db_goal.code = charts[0].code
    result = db.execute(delete(Edit).where(Edit.goal_id == db_goal.id))
    if isinstance(req.instructions, str):
        db_edit = Edit(goal_id=db_goal.id,
                       index=0,
                       edit=req.instructions)
        db.add(db_edit)
    elif isinstance(req.instructions, list):
        index = 0
        for instruction in req.instructions:
            db_edit = Edit(goal_id=db_goal.id,
                           index=index,
                           edit=instruction)
            index += 1
            db.add(db_edit)
    db.commit()

    return {"status": True, "charts": charts,
            "message": f"Successfully edited charts."}


@api.post("/visualize/repair")
@handle_api_exceptions
async def repair_visualization(req: VisualizeRepairWebRequest) -> dict:
    """ Given a visualization goal and some feedback, generate a new visualization that addresses the feedback"""

    charts = lida.repair(
        code=req.code,
        feedback=req.feedback,
        goal=req.goal,
        summary=req.summary,
        textgen_config=req.textgen_config if req.textgen_config else TextGenerationConfig(),
        library=req.library,
        return_error=True
    )

    if len(charts) == 0:
        return {"status": False, "message": "No charts generated"}
    return {"status": True, "charts": charts,
            "message": "Successfully generated chart repairs"}


@api.post("/visualize/explain")
@handle_api_exceptions
async def explain_visualization(req: VisualizeExplainWebRequest,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)) -> dict:
    """Given a visualization code, provide an explanation of the code"""
    textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig(
        n=1,
        temperature=0)

    db_goal = db.query(Goal).filter(Goal.chat_id == req.chat_id, Goal.id == req.goal_id).first()
    if db_goal is None:
        return {"status": False,
                "message": "Goal not found with the given chat_id and question"}

    explanations = lida.explain(
        code=req.code,
        textgen_config=textgen_config,
        library=req.library)

    # save to database
    db_explain = db.query(Explain).filter(Explain.goal_id == db_goal.id).first()
    if db_explain is None:
        db_explain = Explain(goal_id=db_goal.id,
                             explanation={"explanations": explanations[0]})
        db.add(db_explain)
    else:
        db_explain.explanation = {"explanations": explanations[0]}
    db.commit()

    return {"status": True, "explanations": explanations[0],
            "message": "Successfully generated explanations"}


@api.post("/visualize/evaluate")
@handle_api_exceptions
async def evaluate_visualization(req: VisualizeEvalWebRequest,
                                 db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)) -> dict:
    """Given a visualization code, provide an evaluation of the code"""

    db_goal = db.query(Goal).filter(Goal.chat_id == req.chat_id, Goal.question == req.goal.question).first()
    if db_goal is None:
        return {"status": False,
                "message": "Goal not found with the given chat_id and goal"}

    evaluations = lida.evaluate(
        code=req.code,
        goal=req.goal,
        textgen_config=req.textgen_config if req.textgen_config else TextGenerationConfig(
            n=1,
            temperature=0),
        library=req.library)[0]

    # save to database
    db_evaluate = db.query(Evaluate).filter(Evaluate.goal_id == db_goal.id).first()
    if db_evaluate is None:
        db_evaluate = Evaluate(goal_id=db_goal.id,
                               evaluate={"evaluations": evaluations})
        db.add(db_evaluate)
    else:
        db_evaluate.evaluate = {"evaluations": evaluations}
    db.commit()

    return {"status": True, "evaluations": evaluations,
            "message": "Successfully generated evaluation"}


@api.post("/visualize/recommend")
@handle_api_exceptions
async def recommend_visualization(req: VisualizeRecommendRequest) -> dict:
    """Given a dataset summary, generate a visualization recommendations"""

    textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig()
    charts = lida.recommend(
        summary=req.summary,
        code=req.code,
        textgen_config=textgen_config,
        library=req.library,
        return_error=True)

    if len(charts) == 0:
        return {"status": False, "message": "No charts generated"}
    return {"status": True, "charts": charts,
            "message": "Successfully generated chart recommendation"}


@api.post("/visualize/conclusion")
@handle_api_exceptions
async def conclusion_visualization(req: VisualizeConclusionRequest) -> dict:
    """Given a dataset summary, generate a visualization recommendations"""

    textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig()
    charts = lida.conclusion(
        summary=req.summary,
        code=req.code,
        goal=req.goal,
        hint=req.hint,
        library=req.library,
        textgen_config=textgen_config
    )

    if len(charts) == 0:
        return {"status": False, "message": "No charts generated"}
    return {"status": True, "charts": charts,
            "message": "Successfully generated chart conclusion"}


@api.post("/text/generate")
@handle_api_exceptions
async def generate_text(textgen_config: TextGenerationConfig) -> dict:
    """Generate text given some prompt"""
    completions = textgen.generate(textgen_config)
    return {"status": True, "completions": completions.text}


@api.post("/goal")
@handle_api_exceptions
async def generate_goal(req: GoalWebRequest,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)) -> dict:
    """Generate goals given a dataset summary"""
    db_chat = db.query(Chat).filter(Chat.id == req.chat_id, Chat.user_id == current_user.id).first()
    if db_chat is None:
        return {"status": False,
                "message": "Chat not found with the given chat_id"}
    textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig()
    goals = lida.goals(req.summary, n=req.n, textgen_config=textgen_config, hint=req.extra_hint_interest)

    # save to database
    db_chat.extra_hint_interest = req.extra_hint_interest
    for goal in goals:
        db_goal = Goal(chat_id=req.chat_id,
                       index=goal.index,
                       question=goal.question,
                       visualization=goal.visualization,
                       rationale=goal.rationale,
                       is_auto=1)
        db.add(db_goal)
    db.commit()

    return {"status": True, "data": goals,
            "message": f"Successfully generated {len(goals)} goals"}


@api.post("/summarize")
@handle_api_exceptions
async def upload_file(file: UploadFile = Form(...),
                      data: str = Form(...),
                      chat_id: str = Form(...),
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)) -> dict:
    # print(data)
    json_data = json.loads(data)
    # print(json_data)
    data_parsed: DescribeData = DescribeData(**json_data)
    print(file.filename)
    print(data_parsed)
    # return {}

    """ Upload a file and return a summary of the data """
    # allow csv, excel, json
    allowed_types = ["text/csv", "application/vnd.ms-excel", "application/json"]
    allowed_types_ext = ["csv", "xls", "xlsx", "json"]
    # print("file: ", file)
    # check file type
    print(file)

    if file.content_type not in allowed_types and file.filename.split(".")[-1] not in allowed_types_ext:
        return {"status": False,
                "message": f"Uploaded file type ({file.content_type}) not allowed. Allowed types are: csv, excel, json"}

    # save file to files folder
    file_location = os.path.join(data_folder, file.filename)
    # open file without deleting existing contents
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    # summarize
    textgen_config = TextGenerationConfig(n=1, temperature=0)
    summary, unused_hint = lida.summarize(
        data=file_location,
        file_name=file.filename,
        summary_method="llm",
        summary_hint=data_parsed,
        textgen_config=textgen_config)

    # save to database
    if chat_id != "new":
        db_chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
        if db_chat is None:
            return {"status": False,
                    "message": "Chat not found with the given chat_id"}
        db_chat.data_filename = summary['file_name']
        db_chat.dataset_name = summary['name']
        db_chat.dataset_description = summary['dataset_description']
        db_chat.field_names = {"field_names": summary['field_names']}
        db_chat.fields = {"fields": summary['fields']}
    else:
        db_chat = Chat(user_id=current_user.id,
                       name=summary['name'],
                       data_filename=summary['file_name'],
                       dataset_name=summary['name'],
                       dataset_description=summary['dataset_description'],
                       field_names={"field_names": summary['field_names']},
                       fields={"fields": summary['fields']})
        db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    ret = {"status": True, "summary": summary, "data_filename": file.filename,
           "chat_id": db_chat.id}
    if unused_hint:
        ret["warning"] = {
            "message": ",".join(unused_hint) + " fields description unmatched. ",
            "data": unused_hint
        }
    return ret


# upload via url
@api.post("/summarize/url")
@handle_api_exceptions
async def upload_file_via_url(req: SummaryUrlRequest) -> dict:
    """ Upload a file from a url and return a summary of the data """
    url = req.url
    textgen_config = req.textgen_config if req.textgen_config else TextGenerationConfig(
        n=1, temperature=0)
    file_name = url.split("/")[-1]
    file_location = os.path.join(data_folder, file_name)

    # download file
    url_response = requests.get(url, allow_redirects=True, timeout=1000)
    open(file_location, "wb").write(url_response.content)

    summary = lida.summarize(
        data=file_location,
        file_name=file_name,
        summary_method="llm",
        textgen_config=textgen_config)
    return {"status": True, "summary": summary, "data_filename": file_name}


# convert image to infographics


@api.post("/infographer")
@handle_api_exceptions
async def generate_infographics(req: InfographicsRequest) -> dict:
    """Generate infographics using the peacasso package"""
    result = lida.infographics(
        visualization=req.visualization,
        n=req.n,
        style_prompt=req.style_prompt
        # return_pil=req.return_pil
    )
    return {"status": True, "result": result, "message": "Successfully generated infographics"}


# list supported models


@api.get("/models")
def list_models() -> dict:
    return {"status": True, "data": providers, "message": "Successfully listed models"}


@api.get("/getChatList")
@handle_sync_api_exceptions
def get_chats(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)) -> dict:
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).offset(skip).limit(limit).all()
    chat_list = [{"id": chat.id,
                  "name": chat.name,
                  "create_time": chat.create_time,
                  "update_time": chat.update_time} for chat in chats]

    return {"status": True, "chats": chat_list, "message": "Successfully listed chats!"}


@api.get("/getChatInfo/{chat_id}")
@handle_sync_api_exceptions
def get_chat_info(chat_id: str,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)) -> dict:
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        return {"status": False, "message": "No such chat found."}

    file_location = os.path.join(data_folder, chat.data_filename)
    lida.open_data(data=file_location)
    summary = {
        "name": chat.dataset_name,
        "file_name": chat.data_filename,
        "dataset_description": chat.dataset_description,
        "fields": chat.fields.get("fields"),
        "field_names": chat.field_names.get("field_names")
    }
    goals = db.query(Goal).filter(Goal.chat_id == chat_id).all()
    goal_list = [{"index": goal.index,
                  "question": goal.question,
                  "visualization": goal.visualization,
                  "rationale": goal.rationale,
                  "is_auto": goal.is_auto,
                  "id": goal.id} for goal in goals]

    return {"status": True, "summary": summary,
            "data": goal_list, "message": "Successfully get chatInfo!"}


@api.post("/getGoalInfo")
@handle_api_exceptions
async def get_chat_info(req: VisWebRequest,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)) -> dict:
    goal = db.query(Goal).join(Chat, Chat.id == Goal.chat_id) \
        .filter(Goal.id == req.goal_id, Chat.user_id == current_user.id).first()
    if not goal:
        return {"status": False, "message": "No such goal found."}

    charts = lida.vis(
        code_specs=[goal.code],
        summary=req.summary,
        library=goal.library,
        return_error=True,
    )

    edits = db.query(Edit).filter(Edit.goal_id == goal.id).all()
    instructions = [{"index": edit.index,
                     "edit": edit.edit} for edit in edits]

    exp = eva = None
    explain = db.query(Explain).filter(Explain.goal_id == goal.id).first()
    evaluate = db.query(Evaluate).filter(Evaluate.goal_id == goal.id).first()
    if explain:
        exp = explain.explanation["explanations"]
    if evaluate:
        eva = evaluate.evaluate["evaluations"]

    return {"status": True, "charts": charts,
            "instructions": instructions,
            "explanations": exp,
            "evaluations": eva,
            "message": "Successfully get chatInfo!"}


# 登录获取令牌
@api.post("/token")
@handle_sync_api_exceptions
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)) -> dict:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return {"status": False, "message": "Incorrect username or password"}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@api.post("/register")
@handle_sync_api_exceptions
async def register_user(user: UserCreate, db: Session = Depends(get_db)) -> dict:
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        return {"status": False, "message": "Username already registered"}
    create_user(db, user.username, user.password)
    return {"status": True, "message": "Successfully registered user!"}
