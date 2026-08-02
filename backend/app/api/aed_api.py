"""AED 设备路由：CRUD。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import AuthContext, get_current_user, get_session, require_roles
from app.models.aed import AedDevice
from app.schemas.aed import AedCreate, AedOut, AedUpdate

router = APIRouter(prefix="/aed", tags=["AED"])


def _to_out(d: AedDevice) -> AedOut:
    return AedOut(
        id=d.id,
        name=d.name,
        location=d.location,
        latitude=d.latitude,
        longitude=d.longitude,
        available=d.available,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


@router.get("", response_model=list[AedOut])
def list_aed(
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(select(AedDevice).order_by(AedDevice.id.asc())).all()
    return [_to_out(d) for d in rows]


@router.post("", response_model=AedOut, status_code=201)
def create_aed(
    body: AedCreate,
    ctx: AuthContext = Depends(require_roles("ADMIN", "SYSTEM")),
    session: Session = Depends(get_session),
):
    device = AedDevice(
        name=body.name,
        location=body.location,
        latitude=body.latitude,
        longitude=body.longitude,
        available=body.available,
    )
    session.add(device)
    session.commit()
    session.refresh(device)
    return _to_out(device)


@router.get("/{aed_id}", response_model=AedOut)
def get_aed(
    aed_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    device = session.get(AedDevice, aed_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AED 不存在"
        )
    return _to_out(device)


@router.patch("/{aed_id}", response_model=AedOut)
def update_aed(
    aed_id: int,
    body: AedUpdate,
    ctx: AuthContext = Depends(require_roles("ADMIN", "SYSTEM")),
    session: Session = Depends(get_session),
):
    device = session.get(AedDevice, aed_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AED 不存在"
        )
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(device, field, value)
    session.add(device)
    session.commit()
    session.refresh(device)
    return _to_out(device)


@router.delete("/{aed_id}", status_code=204)
def delete_aed(
    aed_id: int,
    ctx: AuthContext = Depends(require_roles("ADMIN", "SYSTEM")),
    session: Session = Depends(get_session),
):
    device = session.get(AedDevice, aed_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AED 不存在"
        )
    session.delete(device)
    session.commit()
    return None
