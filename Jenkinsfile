pipeline{
    agents any
    stages{
        stage('Cloning github repo to jenkins workspace'){
            steps{
                script{
                    echo "Cloning github repo to jenkins workspace....."
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub-token', url: 'https://github.com/amaanrzv39/jenkins_with_gcp_deployment.git']])
                }
            }
        }
    }
}