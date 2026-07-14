tarting command:-

docker run --rm -it `
  -v "${PWD}\frontend:/app" `
  -w /app `
  -p 4200:4200 `
  node:22-alpine `
  sh -c "npm start -- --host 0.0.0.0"

  