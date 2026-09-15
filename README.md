# TalentIQ

## AI-Powered Recruitment & Career Intelligence Platform

TalentIQ combines machine learning, semantic skill intelligence,
document processing, and AI-assisted career intelligence to support
candidate-job suitability analysis and recruitment workflows.

## Core ML Task

TalentIQ predicts:

- Good Fit
- Potential Fit
- No Fit

The system predicts candidate-job suitability rather than hiring
probability.

## Current ML Engine

TalentIQ Hybrid V2 combines:

- TF-IDF textual features
- Structured candidate-job features
- MiniLM semantic features
- Logistic Regression

Total model features: 100,019.

## Application Architecture

React + TypeScript
        |
        v
FastAPI Backend
        |
        +---- ML Inference Engine
        |
        +---- Resume/JD Processing
        |
        +---- PostgreSQL + pgvector
        |
        +---- AI / RAG Services

## Repository Structure

backend/
    app/
        api/
        core/
        schemas/
        services/
        ml/
        db/
    tests/

frontend/
    (planned)

ml/
    (planned)

## Responsible AI

TalentIQ is designed as a decision-support system.

It does not predict hiring probability and should not make
automated hiring decisions without appropriate human review.

Sensitive demographic characteristics are excluded from the
core suitability model.
