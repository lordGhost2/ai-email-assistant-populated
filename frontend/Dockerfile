FROM node:18-alpine
WORKDIR /app
COPY package.json /app/package.json
COPY src /app/src
RUN npm install
EXPOSE 3000
CMD ["npm","run","dev"]
