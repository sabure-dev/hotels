from prometheus_client import Counter

USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total number of user registrations',
    ['status']
)

PASSWORD_RESETS = Counter(
    'password_resets_total',
    'Total number of password reset attempts',
    ['status']
)

EMAIL_VERIFICATIONS = Counter(
    'email_verifications_total',
    'Total number of email verification attempts',
    ['status']
) 