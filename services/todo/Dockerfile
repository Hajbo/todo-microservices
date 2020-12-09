# build environment
FROM node:15.3.0-buster
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
COPY package-lock.json ./
RUN npm ci --silent
COPY . ./
CMD [ "node", "app.js" ]