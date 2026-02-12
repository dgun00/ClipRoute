# Java 17 실행 환경 사용
FROM openjdk:17-jdk-slim

# 빌드된 jar 파일을 컨테이너 내부로 복사
# build/libs/*.jar 파일이 생성되어 있어야 함
COPY build/libs/*.jar app.jar

# 서버 실행 (환경변수는 실행 시점에 주입받음)
ENTRYPOINT ["java", "-jar", "/app.jar"]