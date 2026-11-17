pipeline {
    agent any
    options { timestamps() }
    environment {
        IMAGE_NAME = 'department-performance-dashboard'
        TEST_PORT = '18080'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build image') {
            steps {
                sh 'docker build --pull -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }
        stage('Automated checks') {
            steps {
                sh 'docker run --rm ${IMAGE_NAME}:${BUILD_NUMBER} python -m unittest discover -s tests -v'
            }
        }
        stage('Tag artefact') {
            steps {
                sh '''
                    docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:test
                    docker image inspect ${IMAGE_NAME}:${BUILD_NUMBER}
                    docker image inspect ${IMAGE_NAME}:test
                '''
            }
        }
        stage('Deploy to test') {
            steps {
                sh '''
                    APP_IMAGE=${IMAGE_NAME}:${BUILD_NUMBER} APP_PORT=${TEST_PORT} \
                      docker compose -p department-dashboard-test-${BUILD_NUMBER} up -d --no-build
                '''
            }
        }
        stage('Deployment smoke check') {
            steps {
                sh '''
                    for attempt in $(seq 1 30); do
                      if curl --fail --silent http://localhost:${TEST_PORT}/health; then
                        curl --fail --silent http://localhost:${TEST_PORT}/api/departments
                        exit 0
                      fi
                      sleep 2
                    done
                    docker compose -p department-dashboard-test-${BUILD_NUMBER} logs app db
                    exit 1
                '''
            }
        }
    }
    post {
        always {
            sh 'docker compose -p department-dashboard-test-${BUILD_NUMBER} down -v --remove-orphans || true'
        }
    }
}
