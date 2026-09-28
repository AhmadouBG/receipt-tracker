# Étape 1 : Compilation du projet React

FROM node:22-alpine AS builder

# Enable Corepack to use pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy the package.json and pnpm lockfile
COPY package.json pnpm-lock.yaml* ./

# Disable interactive prompt block for pnpm v10+ build scripts in CI/Docker
ENV PNPM_CONFIG_DANGEROUSLY_ALLOW_ALL_BUILDS=true

# Install dependencies using pnpm (equivalent of npm ci)
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm run build

# Étape 2 : Serveur de production Nginx léger
FROM nginx:alpine
# This stage leaves behind heavy node.js environment and node_modules folder making the final docker image small
COPY --from=builder /app/dist /usr/share/nginx/html
# Configuration personnalisée de Nginx pour gérer le routage React et le proxy API
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://backend:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
# Run Nginx in the foreground so Docker can monitor it, and keep it running even if the terminal session ends.
CMD ["nginx", "-g", "daemon off;"]
