"""Hermes loader entry point for the SDD plugin repository."""

from .hermes_sdd.plugin import register

__all__ = ["register"]
