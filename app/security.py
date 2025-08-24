from passlib.context import CryptContext

# --- Configurações globais ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@staticmethod
def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(raw_password, hashed_password)


@staticmethod
def get_password_hash(password: str) -> str:
    """Gera um hash seguro para a senha informada."""
    return pwd_context.hash(password)
