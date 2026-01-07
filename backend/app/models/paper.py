"""
论文相关的 Pydantic 模型 (API Schema)

定义的模型:
- Author: 作者信息
- PaperBase/PaperCreate/Paper: 论文 CRUD 模型
- PaperSummary: AI 生成的论文摘要
- ArxivPaper: arXiv API 返回的论文格式

使用示例:
    paper = Paper(arxiv_id="2401.12345", title="...", abstract="...")
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================
# Author (作者)
# ============================================
class Author(BaseModel):
    """作者信息"""
    name: str = Field(..., description="作者姓名")
    affiliation: Optional[str] = Field(None, description="所属机构")


# ============================================
# Paper (论文)
# ============================================
class PaperBase(BaseModel):
    """论文基础字段"""
    arxiv_id: str = Field(..., description="arXiv ID (如: 2401.12345)")
    title: str = Field(..., description="论文标题")
    abstract: str = Field(..., description="论文摘要")
    authors: List[Author] = Field(default_factory=list, description="作者列表")
    categories: List[str] = Field(default_factory=list, description="arXiv 分类")
    primary_category: Optional[str] = Field(None, description="主分类")
    pdf_url: Optional[str] = Field(None, description="PDF 链接")
    arxiv_url: Optional[str] = Field(None, description="arXiv 页面链接")
    published_at: Optional[datetime] = Field(None, description="发布时间")


class PaperCreate(PaperBase):
    """创建论文的请求模型"""
    pass


class Paper(PaperBase):
    """完整论文模型 (含 ID, 时间戳)"""
    id: int
    created_at: datetime

    source: str = Field(..., description="来源")
    entry_id: str = Field(..., description="入口ID")
    
    # 租户相关 (可选)
    is_read: Optional[bool] = Field(None, description="是否已读")
    is_starred: Optional[bool] = Field(None, description="是否收藏")
    notes: Optional[str] = Field(None, description="用户笔记")
    saved_at: Optional[datetime] = Field(None, description="保存时间")
    
    class Config:
        from_attributes = True


class PaperList(BaseModel):
    """论文列表响应"""
    items: List[Paper]
    total: int
    page: int = 1
    page_size: int = 20


# ============================================
# Paper Summary (AI 摘要)
# ============================================
class PaperSummary(BaseModel):
    """AI 生成的论文摘要"""
    paper_id: int
    summary: str = Field(..., description="AI 生成的摘要")
    key_points: List[str] = Field(default_factory=list, description="关键点")
    methodology: Optional[str] = Field(None, description="方法论")
    contributions: List[str] = Field(default_factory=list, description="主要贡献")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str = Field(..., description="使用的 LLM 模型")


# ============================================
# arXiv API Response (爬虫用)
# ============================================
class ArxivPaperRaw(BaseModel):
    """arXiv API 返回的原始论文数据"""
    id: str = Field(..., description="arXiv ID (带版本号)")
    title: str
    summary: str = Field(..., alias="abstract")
    authors: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    primary_category: Optional[str] = None
    published: datetime
    updated: Optional[datetime] = None
    pdf_url: Optional[str] = None
    
    def to_paper_create(self) -> PaperCreate:
        """转换为 PaperCreate"""
        # 清理 arXiv ID (去掉版本号)
        arxiv_id = self.id.split("/")[-1]  # 处理旧格式 ID
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.rsplit("v", 1)[0]
        
        return PaperCreate(
            arxiv_id=arxiv_id,
            title=self.title.strip().replace("\n", " "),
            abstract=self.summary.strip().replace("\n", " "),
            authors=[Author(name=name) for name in self.authors],
            categories=self.categories,
            primary_category=self.primary_category,
            pdf_url=self.pdf_url,
            arxiv_url=f"https://arxiv.org/abs/{arxiv_id}",
            published_at=self.published,
        )
