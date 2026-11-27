# syntax=docker/dockerfile:1
ARG GRADLE_IMAGE=gradle:8.14.3-jdk21-alpine
ARG JRE_IMAGE=eclipse-temurin:21.0.9_10-jre-alpine-3.22
FROM ${GRADLE_IMAGE} AS builder
WORKDIR /workspace
COPY settings.gradle build.gradle ./
COPY album/ album/
COPY album-api/ album-api/
COPY recensioni/ recensioni/
COPY recensioni-api/ recensioni-api/
COPY connessioni/ connessioni/
COPY connessioni-api/ connessioni-api/
COPY recensioni-seguite/ recensioni-seguite/
COPY recensioni-seguite-api/ recensioni-seguite-api/
COPY api-gateway/ api-gateway/
ARG SERVICE
RUN case "$SERVICE" in album|recensioni|connessioni|recensioni-seguite|api-gateway) ;; *) exit 1 ;; esac \
    && gradle --no-daemon --max-workers=2 -Dorg.gradle.jvmargs=-Xmx768m ":${SERVICE}:bootJar" \
    && mkdir /out && cp "${SERVICE}/build/libs/${SERVICE}.jar" /out/app.jar

FROM ${JRE_IMAGE} AS runtime
RUN addgroup -S -g 10001 app && adduser -S -D -H -u 10001 -G app app
WORKDIR /app
COPY --from=builder --chown=10001:10001 /out/app.jar /app/app.jar
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
