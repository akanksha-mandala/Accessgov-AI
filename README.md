# AccessGov AI Fix 5

Fixes the registration/authentication contract.

Files:
- backend/api/auth.py — registration now returns a real JWT Token response.
- frontend/src/context/AuthContext.tsx — requires and stores the real JWT + user.
- frontend/src/services/apiClient.ts — local API host follows the frontend host.

Apply to AccessGov-AI-FIXED, restart Uvicorn and Vite, then test registration.
