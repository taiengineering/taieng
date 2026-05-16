FROM node:22-slim
WORKDIR /app
COPY health-check.js .
EXPOSE 3100
CMD ["node", "health-check.js"]
