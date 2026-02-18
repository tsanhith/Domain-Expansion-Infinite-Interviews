from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

ApplicationStatus = Literal["Pending", "Found", "Tailored", "Applied", "Failed"]


class ApplyRequest(BaseModel):
    job_url: HttpUrl


class ApplicationRecord(BaseModel):
    id: int
    job_url: str
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    error_log: str | None = None
    resume_pdf_path: str | None = None


class WorkflowState(BaseModel):
    application_id: int
    job_url: str
    job_description: str = ""
    extracted_skills: list[str] = Field(default_factory=list)
    selected_projects: list[str] = Field(default_factory=list)
    resume_pdf_path: str = ""
    application_status: ApplicationStatus = "Pending"
    error_log: str = ""
