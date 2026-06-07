pipeline{
    agent any
    environment{
        VENV_DIR = "venv"
    }
    stages{
        stage('Cloning github repo to jenkins workspace'){
            steps{
                script{
                    echo "Cloning github repo to jenkins workspace....."
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub-token', url: 'https://github.com/amaanrzv39/jenkins_with_gcp_deployment.git']])
                }
            }
        }
        stage('Setting up virtual environment and installing dependencies'){
            steps{
                script{
                    echo "Setting up virtual environment and installing dependencies....."
                    sh '''
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
                }
            }
        }
    }
}