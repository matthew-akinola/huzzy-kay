pipeline {
	agent any
  
	stages {
		stage("Deploy backend"){

			steps {
				sh "sudo systemctl restart starfinder-backend.service"
			} 	
	   }
	}
}
