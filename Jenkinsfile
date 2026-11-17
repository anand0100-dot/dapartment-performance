pipeline {
    agent any
    options { timestamps() }
    environment {
        COMPOSE_PROJECT_NAME = 'department-dashboard-ci'
        APP_PORT = '18080'
    }
    stages {
        stage('Build image') {
            steps { sh 'docker compose build app' }
        }
        stage('Deploy simulation') {
            steps { sh 'docker compose up -d' }
        }
        stage('Smoke check') {
            steps {
                sh '''
                    for attempt in $(seq 1 30); do
                      if curl --fail --silent http://localhost:18080/health; then exit 0; fi
                      sleep 2
                    done
                    docker compose logs app db
                    exit 1
                '''
            }
        }
    }
    post {
        always { sh 'docker compose down -v --remove-orphans' }
    }
}
