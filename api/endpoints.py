API_PREFIX = "/api"

ENDPOINTS = {
    "login": f"{API_PREFIX}/login",
    "dashboard": f"{API_PREFIX}/dashboard",
    "products": f"{API_PREFIX}/products",
    "product": f"{API_PREFIX}/products/{id}",
    "customers": f"{API_PREFIX}/customers",
    "customer": f"{API_PREFIX}/customers/{id}",
    "quotes": f"{API_PREFIX}/quotes",
    "quote": f"{API_PREFIX}/quotes/{id}",
    "invoices": f"{API_PREFIX}/invoices",
    "invoice": f"{API_PREFIX}/invoices/{id}",
    "delivery_notes": f"{API_PREFIX}/delivery_notes",
    "delivery_note": f"{API_PREFIX}/delivery_notes/{id}",
    "payments": f"{API_PREFIX}/payments",
    "payment": f"{API_PREFIX}/payments/{id}",
}
