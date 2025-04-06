curl -X POST http://127.0.0.1:5000/api/chat \
-H "Authorization: Bearer <your-jwt-token>" \
-H "Content-Type: application/json" \
-d '{"userId": "123", "messages": [{"role": "user", "content": "Hello"}]}'

curl -X POST http://127.0.0.1:5000/api/auth \
-H "Authorization: <API_AUTH_KEY>" \
-H "Content-Type: application/json" \
-d '{"userId": "123"}'