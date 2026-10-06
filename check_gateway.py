"""Check the documented GenzShop gateway without printing credentials or errors."""
from lab.model import make_model

if __name__ == "__main__":
    try:
        model = make_model()
        print("Endpoint:", str(model.root_client.base_url))
        models = model.root_client.models.list()
        print("Available models:", ", ".join(m.id for m in models.data))
    except Exception as exc:
        print("Gateway check failed:", type(exc).__name__, "status=", getattr(exc, "status_code", None))
        raise SystemExit(1)
