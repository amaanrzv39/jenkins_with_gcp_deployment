// pipeline{
//     agent any
//     environment{
//         VENV_DIR = "venv"
//         GCP_PROJECT = "project-cd8d3620-549d-44e4-ba7"
//         GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
//     }
//     stages{
//         stage('Cloning github repo to jenkins workspace'){
//             steps{
//                 script{
//                     echo "Cloning github repo to jenkins workspace....."
//                     checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub-token', url: 'https://github.com/amaanrzv39/jenkins_with_gcp_deployment.git']])
//                 }
//             }
//         }
//         stage('Setting up virtual environment and installing dependencies'){
//             steps{
//                 script{
//                     echo "Setting up virtual environment and installing dependencies....."
//                     sh '''
//                     python3 -m venv ${VENV_DIR}
//                     . ${VENV_DIR}/bin/activate
//                     pip install --upgrade pip
//                     pip install -r requirements.txt
//                     '''
//                 }
//             }
//         }
//         stage('Building and pushing docker image to gcr'){
//             steps{
//                 withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
//                     script{
//                         echo "Building and pushing docker image to gcr....."
//                         sh '''
//                         export PATH=$PATH:${GCLOUD_PATH}
//                         gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
//                         gcloud config set project ${GCP_PROJECT}
//                         gcloud auth configure-docker --quiet
//                         docker build -t gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest .
//                         docker push gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest
//                         '''
//                     }
//                 }
//             }
//         }
//     }
// }



pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "project-cd8d3620-549d-44e4-ba7"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub-token', url: 'https://github.com/amaanrzv39/jenkins_with_gcp_deployment.git']])
                }
            }
        }

        stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}


                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud auth configure-docker --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest .

                        docker push gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest 

                        '''
                    }
                }
            }
        }


        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.............'
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}


                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy hotel-reservation-prediction \
                            --image=gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest \
                            --platform=managed \
                            --region=us-central1 \
                            --allow-unauthenticated
                            
                        '''
                    }
                }
            }
        }
        
    }
}