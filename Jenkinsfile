pipeline {
    agent any

    tools {
        jdk "jdk-21"
        nodejs "nodejs-25"
    }
    
    environment {
        JAVA_HOME = "${tool 'jdk-21'}"
        PATH = "${JAVA_HOME}/bin:${env.PATH}"
        // DOCKER_CREDENTIALS_ID = 'DOCKER_HUB_CREDENTIALS' 
        DOCKER_IMAGE_NAME = 'devsecops-gatepass' 
        CONTAINER_NAME = 'devsecops-gatepass-container'
        CONTAINER_PORT = '8000'
        HOST_PORT = '8000'
    }


    stages {
        stage ("clean workspace") {
            steps {
                cleanWs()
            }
        }
        stage('github checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/jsasi2004/clinic_appointment.git'
            }
        }
        stage('trivy scan') {
            steps {
                sh '''
                    mkdir -p contrib
                    curl -sSL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o contrib/html.tpl
        
                    trivy fs . \
                        --severity HIGH,CRITICAL \
                        --format template \
                        --template "@contrib/html.tpl" \
                        --output trivy-fs-report.html
                '''
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '--format HTML', odcInstallation: 'dependency-check'
            }
        }

        // stage('Sonar Analysis') {
        //     steps {
        //         withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
        //         withSonarQubeEnv('SonarCloud') {
        //             script {
        //             // Install or use a SonarScanner tool configured in Jenkins
        //             // Assuming you have a SonarScanner installation named "sonar-scanner"
        //             def scannerHome = tool name: 'SonarScannerCloud', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    
        //             // Run the scanner
        //             sh """${scannerHome}/bin/sonar-scanner \
        //                 -Dsonar.login=${SONAR_TOKEN} \
        //                 -Dsonar.projectKey=kanna-hub2142_devsecops-gatepass-app \
        //                 -Dsonar.organization=kanna-hub2142 \
        //                 -Dsonar.host.url=https://sonarcloud.io \
        //                 -Dsonar.sources=. \
        //                 -Dsonar.nodejs.executable=\$(which node) \
        //                 -Dsonar.scanner.skipNodeProvisioning=true \
        //                 -Dsonar.java.binaries=target/** """
        //             }
        //         }
        //         }
        //     }
        // }

        // stage('Docker login') {
        //     steps {
        //         script {
        //             withCredentials([
        //                 usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')
        //                 ]) {
        //                     sh "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin"
        //                 }
        //                 sh "Login successful......."
        //         }
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                script {
                    
                    sh "docker build -t knnkshr/${DOCKER_IMAGE_NAME}:latest ."
                }
            }
        }

        stage('trivy docker image scan') {
            steps {
                sh "trivy image --format table -o trivy_report.html --exit-code 0 --severity HIGH,CRITICAL knnkshr/${DOCKER_IMAGE_NAME}:latest"
            }
        }

        // stage('Push Docker Image') {
        //     steps {
        //         script {
        //         docker.withRegistry('', "${DOCKER_CREDENTIALS_ID}") {
        //             sh "docker push knnkshr/${DOCKER_IMAGE_NAME}:latest"
        //         }
        //         }
        //     }
        // }

        stage("Stopping Old Container") {
            steps {
                script {
                  sh "docker stop ${CONTAINER_NAME} || true"
                }
            }
        }

        stage("Removing Old Container") {
            steps {
                script {
                  sh "docker rm ${CONTAINER_NAME} || true"
                }
            }
        }

        // stage('Run Docker Container with Django Superuser') {
        //     steps {
        //         // Bind all four secrets from Jenkins credentials
        //         withCredentials([
        //         string(credentialsId: 'DJANGO_SUPERUSER_USERNAME', variable: 'DJANGO_SUPERUSER_USERNAME'),
        //         string(credentialsId: 'DJANGO_SUPERUSER_PASSWORD', variable: 'DJANGO_SUPERUSER_PASSWORD'),
        //         string(credentialsId: 'DJANGO_SUPERUSER_EMAIL',    variable: 'DJANGO_SUPERUSER_EMAIL'),
        //         string(credentialsId: 'DJANGO_SUPERUSER_FIRSTNAME', variable: 'DJANGO_SUPERUSER_FIRSTNAME'),
        //         string(credentialsId: 'DJANGO_SUPERUSER_LASTNAME',  variable: 'DJANGO_SUPERUSER_LASTNAME'),
        //         string(credentialsId: 'DB_USER',  variable: 'DB_USER'),
        //         string(credentialsId: 'DB_PASSWORD',  variable: 'DB_PASSWORD'),
        //         string(credentialsId: 'DB_HOST',  variable: 'DB_HOST'),
        //         string(credentialsId: 'DB_PORT',  variable: 'DB_PORT'),
        //         string(credentialsId: 'DB_NAME',  variable: 'DB_NAME'),
        //         string(credentialsId: 'DATABASE_URL',  variable: 'DATABASE_URL')
        //         ]) {
        //         sh """
        //             docker run -d \\
        //             --name ${CONTAINER_NAME} \\
        //             -e DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME} \\
        //             -e DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD} \\
        //             -e DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL} \\
        //             -e DJANGO_SUPERUSER_FIRSTNAME=${DJANGO_SUPERUSER_FIRSTNAME} \\
        //             -e DJANGO_SUPERUSER_LASTNAME=${DJANGO_SUPERUSER_LASTNAME} \\
        //             -e DB_NAME=${DB_NAME} \\
        //             -e DB_HOST=${DB_HOST} \\
        //             -e DB_PORT=${DB_PORT} \\
        //             -e DB_USER=${DB_USER} \\
        //             -e DB_PASSWORD=${DB_PASSWORD} \\
        //             -e DATABASE_URL=${DATABASE_URL} \\
        //             -p 8000:8000 \\
        //             knnkshr/${DOCKER_IMAGE_NAME}:latest
        //         """
        //         }
        //     }
        // }
    }
}
