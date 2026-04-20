"""Placeholder for halftone signals.

Image processing is dispatched explicitly from the views to Celery, so we
do not auto-trigger anything from `post_save` here. The module exists to
keep the AppConfig.ready() import contract stable and ready for future
hooks (e.g. cleanup of stale jobs).
"""
