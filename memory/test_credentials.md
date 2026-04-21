# Test Credentials

## Emergent-Managed Google OAuth

The app uses Emergent-Managed Google Authentication. The UI login path (`/login` → `auth.emergentagent.com`) cannot be completed by automated tests. For API testing, use the seeded bearer token below.

## Seeded Test Session (for automated API tests)

Run `python3 /app/backend/seed_test_session.py` before testing to seed:

- **Email**: `test-restoration@emaira.art`
- **Role**: `user`
- **Subscription Tier**: `collectors_advisory` (unlocks Restoration Studio)
- **Bearer Token**: `TEST_SESSION_TOKEN_RESTORATION_2026`

### Usage with curl

```bash
curl -X GET "$API_URL/api/auth/me" \
  -H "Authorization: Bearer TEST_SESSION_TOKEN_RESTORATION_2026"
```

### Usage in Playwright (set as cookie)

```python
await context.add_cookies([{
    "name": "session_token",
    "value": "TEST_SESSION_TOKEN_RESTORATION_2026",
    "domain": "vr-storyteller.preview.emergentagent.com",
    "path": "/",
    "secure": True,
    "sameSite": "None",
}])
```

## Superadmin (production)

- **Email**: `rohankaji@gmail.com` — granted `super_admin` role upon first Google sign-in via the normal OAuth flow. Cannot be pre-seeded because the real session_token is minted by Emergent Auth service.
