FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Dev server with hot reload. For a production image you'd add a second
# stage that runs `npm run build` and serves the static output via nginx —
# noted in docs/architecture.md as a documented future improvement.
CMD ["npm", "run", "dev"]
