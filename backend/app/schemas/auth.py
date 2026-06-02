"""Schemas Pydantic para autenticación."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_code: str = Field(min_length=1, max_length=64)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TwoFactorChallengeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requires_2fa: bool
    challenge_id: str


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1)


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str
    tenant_id: str
    roles: list[str]


class TotpEnrollmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    secret: str
    current_code: str


class TotpVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=6, max_length=6)


class TotpChallengeRequest(TotpVerifyRequest):
    challenge_id: str


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_code: str = Field(min_length=1, max_length=64)
    email: str = Field(min_length=3, max_length=255)


class ForgotPasswordResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    recovery_token: str | None = None


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
