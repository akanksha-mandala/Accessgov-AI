"""Persist document intelligence inspection results.

Revision ID: 7f4c2d91a8b3
Revises: 01dbee19d90a
"""

from alembic import op
import sqlalchemy as sa


revision = "7f4c2d91a8b3"
down_revision = "01dbee19d90a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "uploaded_documents",
        sa.Column("ocr_status", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("ocr_confidence", sa.Float(), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("readability_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("sharpness_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("readiness_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("quality_issues", sa.JSON(), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("extracted_fields", sa.JSON(), nullable=True),
    )
    op.add_column(
        "uploaded_documents",
        sa.Column("validation_errors", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("uploaded_documents", "validation_errors")
    op.drop_column("uploaded_documents", "extracted_fields")
    op.drop_column("uploaded_documents", "quality_issues")
    op.drop_column("uploaded_documents", "readiness_score")
    op.drop_column("uploaded_documents", "sharpness_score")
    op.drop_column("uploaded_documents", "readability_score")
    op.drop_column("uploaded_documents", "ocr_confidence")
    op.drop_column("uploaded_documents", "ocr_status")
