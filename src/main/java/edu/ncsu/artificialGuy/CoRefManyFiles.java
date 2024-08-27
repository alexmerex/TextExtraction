/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package edu.ncsu.artificialGuy;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

/**
 *
 * @author DOPHUC
 */
public class CoRefManyFiles {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // TODO code application logic here
        // TODO code application logic here
        String PathName = "inputcoref";
        File folder = new File(PathName);
        File[] listOfFiles = folder.listFiles();
        System.out.println("\n DEMO FILE");
        System.out.println("===============================================");
        System.out.println("List all files in Folder " + PathName);
        ArrayList<String> FileInList = new ArrayList<String>();
//        File file = new File (StoryFile);
        int Stt = 1;
        // to perform any NLP operations required
        NLP nlp = NLP.getInstance();
        for (File file : listOfFiles) {
            if (file.isFile()) {
//                System.out.println(file.getName());
                String StoryFile = PathName + "/" + file.getName();
                
                System.out.println(Stt + "-story file : " + StoryFile);
                Stt += 1;
                // build a Story object
                Story story = new Story(file);

                // display the original story
                System.out.println("\n######################## ORIGINAL STORY ##########################");
                System.out.println(story.getText().replace(". ", ".\n"));
                System.out.println("##################################################################\n");

                // to perform any NLP operations required
//		NLP nlp = NLP.getInstance();
                // resolve co reference
                String coRefText = nlp.resolveCoRef(story.getText());

                // story after co reference resolution
                System.out.println("\n################# AFTER COREFERENCE RESOLUTION ###################");
                System.out.println(coRefText.replace(". ", ".\n"));
                ///////////
                String FileNameOut = "Coref_" + file.getName();
                String PathOut = "outputcoref/";
                String filePathOut = PathOut + FileNameOut;
                System.out.println("\n\n\nWrite discover triples to file " + filePathOut);
                ////
                try {
                    FileWriter myWriter = new FileWriter(filePathOut);
                    myWriter.write(coRefText.replace(". ", ".\n"));
                    myWriter.close();
                    System.out.println("Successfully wrote to the file " + filePathOut);
                } catch (IOException e) {
                    System.out.println("An error occurred.");
                    e.printStackTrace();
                }
                
                System.out.println("====Done======");    ////////////////
            }
        }
        
    }
    
}
