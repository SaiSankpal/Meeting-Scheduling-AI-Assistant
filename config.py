import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Centralized Configuration Object"""

    #LLM KEY
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

    # GOOGLE CALENDAR
    GOOGLE_CREDENTIALS_FILE: str = os.getenv(
        "GOOGLE_CREDENTIALS_FILE", "credentials.json"
    )

    GOOGLE_TOKEN_FILE: str = os.getenv(
        "GOOGLE_TOKEN_FILE", "token.json"
    )

    #APP SETTINGS
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    #VALIDATION
    @staticmethod
    def validate():
        """Ensure required environment variables exist."""
        if not Settings.GROQ_API_KEY:
            raise ValueError(
                "No LLM API key found. Set GROQ_API_KEY in .env"
            )


#global instance
settings = Settings()

#validate at startup
settings.validate()


