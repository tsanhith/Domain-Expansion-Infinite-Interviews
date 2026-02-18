from __future__ import annotations

import json
import re
from typing import Any, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI

from app import db
from app.schemas import WorkflowState
from app.settings import settings


class GraphState(TypedDict):
    application_id: int
    job_url: str
    job_description: str
    extracted_skills: list[str]
    selected_projects: list[str]
    resume_pdf_path: str
    application_status: str
    error_log: str


class DomainWorkflow:
    """LangGraph-backed workflow for deterministic multi-step execution."""

    def __init__(self) -> None:
        graph = StateGraph(GraphState)
        graph.add_node("scout", self.scout_node)
        graph.add_node("strategist", self.strategist_node)
        graph.add_node("adapter", self.adapter_node)
        graph.add_node("executioner", self.executioner_node)

        graph.add_edge(START, "scout")
        graph.add_edge("scout", "strategist")
        graph.add_edge("strategist", "adapter")
        graph.add_edge("adapter", "executioner")
        graph.add_edge("executioner", END)

        self._graph = graph.compile()

    def run(self, state: WorkflowState) -> WorkflowState:
        payload: GraphState = {
            "application_id": state.application_id,
            "job_url": state.job_url,
            "job_description": state.job_description,
            "extracted_skills": state.extracted_skills,
            "selected_projects": state.selected_projects,
            "resume_pdf_path": state.resume_pdf_path,
            "application_status": state.application_status,
            "error_log": state.error_log,
        }
        final_state = self._graph.invoke(payload)
        return WorkflowState(**final_state)

    def scout_node(self, state: GraphState) -> GraphState:
        state["job_description"] = (
            "We are hiring a full-stack AI developer with Python, FastAPI, "
            "React, SQL, and LLM integration experience."
        )
        state["application_status"] = "Found"
        db.update_application(state["application_id"], "Found")
        return state

    def strategist_node(self, state: GraphState) -> GraphState:
        model = self._build_llm()
        if model is not None:
            prompt = (
                "Extract skills and choose matching project themes for this JD. "
                "Return strict JSON with keys extracted_skills (list[str]) and selected_projects (list[str]).\n"
                f"JD:\n{state['job_description']}"
            )
            response = model.invoke(prompt)
            content = self._response_text(response)
            parsed = self._safe_parse_json(content)
        if settings.openai_api_key:
            prompt = (
                "Extract skills and choose matching project themes for this JD. "
                "Return JSON with keys extracted_skills (list[str]) and selected_projects (list[str]).\n"
                f"JD:\n{state['job_description']}"
            )
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            response = model.invoke(prompt)
            parsed = self._safe_parse_json(response.content)
            state["extracted_skills"] = parsed.get("extracted_skills", [])
            state["selected_projects"] = parsed.get("selected_projects", [])

        if not state["extracted_skills"]:
            text = state["job_description"].lower()
            vocab = ["python", "fastapi", "react", "sql", "llm", "langgraph", "playwright"]
            state["extracted_skills"] = [s for s in vocab if re.search(rf"\b{s}\b", text)]

        if not state["selected_projects"]:
            projects: list[str] = []
            if "fastapi" in state["extracted_skills"] or "python" in state["extracted_skills"]:
                projects.append("Backend APIs with Python/FastAPI")
            if "react" in state["extracted_skills"]:
                projects.append("Frontend dashboard with React/Tailwind")
            if "llm" in state["extracted_skills"]:
                projects.append("LLM workflow automation projects")
            state["selected_projects"] = projects or ["General software engineering projects"]

        state["application_status"] = "Tailored"
        db.update_application(state["application_id"], "Tailored")
        return state

    def adapter_node(self, state: GraphState) -> GraphState:
        state["resume_pdf_path"] = f"artifacts/resume_{state['application_id']}.pdf"
        return state

    def executioner_node(self, state: GraphState) -> GraphState:
        state["application_status"] = "Applied"
        db.update_application(
            state["application_id"],
            "Applied",
            resume_pdf_path=state["resume_pdf_path"],
        )
        return state

    def _build_llm(self) -> Any | None:
        if settings.llm_provider == "google" and settings.google_api_key:
            return ChatGoogleGenerativeAI(model=settings.llm_model, temperature=0)

        if settings.llm_provider == "openai" and settings.openai_api_key:
            return ChatOpenAI(model=settings.llm_model, temperature=0)

        return None

    def _response_text(self, response: Any) -> str:
        content = getattr(response, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    parts.append(str(item["text"]))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(content)

    def _safe_parse_json(self, content: str) -> dict:
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
