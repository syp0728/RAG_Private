FROM node:20-alpine

WORKDIR /app

# 의존성 설치
COPY package.json .
RUN npm install

# 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

# 포트 노출
EXPOSE 3000

# 개발 서버 실행 (또는 빌드된 정적 파일 제공)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]

