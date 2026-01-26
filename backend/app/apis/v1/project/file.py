"""
项目文件管理API
支持上传和下载项目相关文件（PDF、Word等）
"""
import os
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Path as PathParameter
from fastapi.responses import FileResponse
from typing import List

from app.apis.deps import get_current_user, get_gm_user
from app.models.project import ProjectInfo
from app.schemas.base import BaseOut

app = APIRouter()

# 文件存储根目录
UPLOAD_DIR = Path("static")
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_project_dir(project_name: str) -> Path:
    """获取项目文件目录，如果不存在则创建"""
    project_dir = UPLOAD_DIR / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def is_allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.post("/{project_id}/upload", response_model=BaseOut, description='上传项目文件', summary='上传项目文件')
async def upload_file(
    project_id: UUID = PathParameter(..., description='项目ID'),
    file: UploadFile = File(..., description='上传的文件'),
    current_user: dict = Depends(get_gm_user)  # 只有GM和ADMIN可以上传
):
    """
    上传项目文件
    - 支持格式：PDF, Word, Excel, PowerPoint, TXT
    - 最大文件大小：50MB
    - 文件存储路径：static/{项目名称}/{文件名}
    - 不会修改项目的content字段
    """
    try:
        # 检查项目是否存在
        project = await ProjectInfo.get_or_none(id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 检查文件扩展名
        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f'不支持的文件格式。允许的格式：{", ".join(ALLOWED_EXTENSIONS)}'
            )
        
        # 读取文件内容
        content = await file.read()
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f'文件大小超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）'
            )
        
        # 获取项目目录
        project_dir = get_project_dir(project.name)
        
        # 保存文件
        file_path = project_dir / file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 不再更新项目的content字段
        
        return BaseOut(message=f'文件上传成功：{file.filename}', count=1)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'文件上传失败：{str(e)}')


@app.get("/{project_id}/files", description='获取项目文件列表', summary='获取项目文件列表')
async def list_files(
    project_id: UUID = PathParameter(..., description='项目ID'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取项目的所有文件列表
    返回文件名、大小、修改时间等信息
    """
    try:
        # 检查项目是否存在
        project = await ProjectInfo.get_or_none(id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 获取项目目录
        project_dir = get_project_dir(project.name)
        
        # 获取文件列表
        files = []
        if project_dir.exists():
            for file_path in project_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'size': stat.st_size,
                        'modified_time': stat.st_mtime,
                    })
        
        return {
            'message': '成功',
            'project_name': project.name,
            'files': files,
            'count': len(files)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'获取文件列表失败：{str(e)}')


@app.get("/{project_id}/download/{filename}", description='下载项目文件', summary='下载项目文件')
async def download_file(
    project_id: UUID = PathParameter(..., description='项目ID'),
    filename: str = PathParameter(..., description='文件名'),
    current_user: dict = Depends(get_current_user)  # 所有登录用户都可以下载
):
    """
    下载项目文件
    - IT和MANUAL角色可以下载
    - 文件从 static/{项目名称}/{文件名} 读取
    """
    try:
        # 检查项目是否存在
        project = await ProjectInfo.get_or_none(id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 获取文件路径
        project_dir = get_project_dir(project.name)
        file_path = project_dir / filename
        
        # 检查文件是否存在
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail='文件不存在')
        
        # 返回文件
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'文件下载失败：{str(e)}')


@app.delete("/{project_id}/delete/{filename}", response_model=BaseOut, description='删除项目文件', summary='删除项目文件')
async def delete_file(
    project_id: UUID = PathParameter(..., description='项目ID'),
    filename: str = PathParameter(..., description='文件名'),
    current_user: dict = Depends(get_gm_user)  # 只有GM和ADMIN可以删除
):
    """
    删除项目文件
    只有项目管理员（GM和ADMIN）可以删除文件
    """
    try:
        # 检查项目是否存在
        project = await ProjectInfo.get_or_none(id=project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 获取文件路径
        project_dir = get_project_dir(project.name)
        file_path = project_dir / filename
        
        # 检查文件是否存在
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail='文件不存在')
        
        # 删除文件
        file_path.unlink()
        
        return BaseOut(message=f'文件删除成功：{filename}', count=1)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'文件删除失败：{str(e)}')
