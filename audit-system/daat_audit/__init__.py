"""Système d'audit automatique du site public daattorah.com.

Phase 1 — MVP en lecture seule (mode ``audit_readonly``) :
exploration des simanim 242 à 269, français, niveau « base »,
archivage versionné des pages, détection des changements.

Ce paquet n'écrit JAMAIS sur le site public ni dans les sources du site.
Voir ``daat_audit.safety`` pour les garde-fous.
"""

__version__ = "0.1.0"
