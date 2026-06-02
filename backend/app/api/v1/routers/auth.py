"""Router de autenticación."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import (
    CurrentUserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
    TotpChallengeRequest,
    TotpEnrollmentResponse,
    TotpVerifyRequest,
    TwoFactorChallengeResponse,
)
from app.services.auth import AuthService, AuthenticationError, CurrentUser, InactiveUserError, RateLimitExceededError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse | TwoFactorChallengeResponse)
async def login(payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip_address = request.client.host if request.client is not None else "unknown"
    try:
        result = await AuthService(db).login(
            tenant_code=payload.tenant_code,
            email=payload.email,
            password=payload.password,
            ip_address=ip_address,
        )
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many attempts") from exc
    except InactiveUserError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user") from exc
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    if result.requires_2fa:
        return TwoFactorChallengeResponse(requires_2fa=True, challenge_id=str(result.challenge_id))
    return TokenResponse(access_token=result.access_token or "", refresh_token=result.refresh_token or "")


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(
        user_id=str(current_user.user_id), tenant_id=str(current_user.tenant_id), roles=current_user.roles
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        result = await AuthService(db).refresh(payload.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
    return TokenResponse(access_token=result.access_token or "", refresh_token=result.refresh_token or "")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: RefreshRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await AuthService(db).logout(payload.refresh_token, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/2fa/enroll", response_model=TotpEnrollmentResponse)
async def enroll_totp(
    current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> TotpEnrollmentResponse:
    secret, current_code = await AuthService(db).enroll_totp(current_user)
    return TotpEnrollmentResponse(secret=secret, current_code=current_code)


@router.post("/2fa/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_totp(
    payload: TotpVerifyRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        await AuthService(db).verify_totp_enrollment(current_user, payload.code)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/2fa/challenge", response_model=TokenResponse)
async def complete_totp_challenge(payload: TotpChallengeRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        result = await AuthService(db).complete_totp_challenge(UUID(payload.challenge_id), payload.code)
    except (AuthenticationError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid challenge") from exc
    return TokenResponse(access_token=result.access_token or "", refresh_token=result.refresh_token or "")


@router.post("/forgot", response_model=ForgotPasswordResponse, status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)) -> ForgotPasswordResponse:
    await AuthService(db).forgot_password(tenant_code=payload.tenant_code, email=payload.email)
    return ForgotPasswordResponse(message="If the account exists, recovery instructions were sent")


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)) -> Response:
    try:
        await AuthService(db).reset_password(token=payload.token, new_password=payload.new_password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid recovery token") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
