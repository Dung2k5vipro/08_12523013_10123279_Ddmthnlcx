FROM node:20-alpine AS deps

WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS runtime

ARG PORT=8000
ENV NODE_ENV=production
ENV PORT=${PORT}

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package*.json ./
COPY src ./src

USER node

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
	CMD node -e "const http=require('http'); const request=http.get({hostname:'127.0.0.1',port:process.env.PORT,path:'/api/health'},response=>process.exit(response.statusCode===200?0:1)); request.on('error',()=>process.exit(1)); request.setTimeout(4000,()=>{request.destroy();process.exit(1);});"

CMD ["node", "src/app.js"]
