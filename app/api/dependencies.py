"""
Application Dependencies

Creates singleton instances of all core components.

These are initialized once when the FastAPI application starts
and reused for every request.
"""

from __future__ import annotations

from app.planner.planner import Planner

from app.retrieval.retriever import Retriever

from app.generation.context_builder import ContextBuilder
from app.generation.generator import LLMGenerator
from app.generation.verifier import ResponseVerifier
from app.generation.formatter import ResponseFormatter


class ApplicationContainer:
    """
    Holds shared application objects.
    """

    def __init__(self):

        self.planner = Planner()

        self.retriever = Retriever()

        self.context_builder = ContextBuilder()

        self.generator = LLMGenerator()

        self.verifier = ResponseVerifier()

        self.formatter = ResponseFormatter()

    # -----------------------------------------------------

    @property
    def ready(self) -> bool:

        return True


# ---------------------------------------------------------
# Singleton Container
# ---------------------------------------------------------

_container: ApplicationContainer | None = None


def get_container() -> ApplicationContainer:
    """
    Return the shared application container.

    Initializes it on first use.
    """

    global _container

    if _container is None:

        print("Initializing application...")

        _container = ApplicationContainer()

        print("Application initialized.")

    return _container


# ---------------------------------------------------------
# Dependency Getters
# ---------------------------------------------------------

def get_planner() -> Planner:

    return get_container().planner


def get_retriever() -> Retriever:

    return get_container().retriever


def get_context_builder() -> ContextBuilder:

    return get_container().context_builder


def get_generator() -> LLMGenerator:

    return get_container().generator


def get_verifier() -> ResponseVerifier:

    return get_container().verifier


def get_formatter() -> ResponseFormatter:

    return get_container().formatter