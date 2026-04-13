"""
独立的ClientInfo模型定义
用于医学验证实验，不依赖外部项目
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientInfo:
    """简化的客户端信息模型"""
    userId: str
    displayName: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str
    deviceType: str = "ANDROID"
    online: bool = True
    lastSeenTs: int = 0
    assignedRole: Optional[str] = None
    patientCandidate: bool = False
    isPatient: bool = False
    fitness: Optional[float] = None  # 体能评分
    # 位置信息（用于距离计算）
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # 简化距离（米）- 与患者之间的距离
    distance: Optional[int] = None


# 导入原项目的ClientInfo（如果可用）
def get_client_info_class():
    """获取ClientInfo类，优先使用项目中的定义"""
    try:
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent / "software_innovation" / "Semifinal" / "project" / "server（云端服务）"
        sys.path.insert(0, str(project_root))
        from app.models.schemas import ClientInfo as OriginalClientInfo
        return OriginalClientInfo
    except ImportError:
        return ClientInfo


# 直接导出
__all__ = ['ClientInfo', 'get_client_info_class']