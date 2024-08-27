Ref: https://stackoverflow.com/questions/58411279/java-with-maven-wouldnt-build-cannot-run-program-cmd-malformed-argument-has

1. First exit netbeans IDE if it's open, then open netbeans configuration file from here: 
   netbeans-Install-Dir/etc/netbeans.conf
2. Add the below arguments:
   -J-Djdk.lang.Process.allowAmbiguousCommands=true
   to the beginning of the string that you find at this line:
   netbeans_default_options="-J-client -J-Xss2m -J-Xms32m ......."
3. Save the change and start your netbeans IDE.

4. Download, install maven, and declare MAVEN_HOME variable. Add the installed maven folder to PATH variable.

5. In NetBeans, choose Tools -> Options -> Execution -> Maven Home: choose the installed maven folder.