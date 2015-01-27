package eu.crowdrec.recs.mahout;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.StringReader;

import javax.json.Json;
import javax.json.JsonObject;
import javax.json.JsonReader;

import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;


public class InternalDataModel {

	
	private File ratings_file;
	private BufferedWriter ratings_writer = null;
	
	public InternalDataModel(String outdir, String userratingFilename) throws IOException {
		ratings_file = new File(outdir + File.separator + userratingFilename);
		ratings_writer = new BufferedWriter(new FileWriter(ratings_file));
	}
	
	public FileDataModel getMahoutFileDataModel() throws IOException {
		ratings_writer.close();
		return new FileDataModel(ratings_file);
	}
	
	protected synchronized boolean writeRelation( byte[] message, boolean writeData) throws NumberFormatException, IOException {
		
			String line = new String(message, "UTF-8");
			
			String user_etype = "user";
			String movie_etype = "movie";
			String rating_rtype = "rating.explicit";
			String eof = "EOF";
			
				String[] els = line.split("\t");
				String rtype = els[0];

				if ( rtype.equals(rating_rtype) ) {
					
					String props = els[3];
					String links = els[4];

					String userid = null;
					String itemid = null;
					double ratingscore = 0;

					if ( props != null ) {
						JsonReader props_reader = Json.createReader(new StringReader(props));
						JsonObject props_json = props_reader.readObject();
						props_reader.close();

						ratingscore = props_json.getInt("rating", 0);
					}

					if ( links != null ) {
						JsonReader links_reader = Json.createReader(new StringReader(links));
						JsonObject links_json = links_reader.readObject();
						links_reader.close();

						String subject = links_json.getString("subject", null);
						String object = links_json.getString("object", null);
						if (subject != null) {
							String etype = subject.split(":")[0];
							String eid = subject.split(":")[1];
							if (etype.equals(user_etype)) {
								userid = eid;
							}
						}
						if (object != null) {
							String etype = object.split(":")[0];
							String eid = object.split(":")[1];
							if (etype.equals(movie_etype)) {
								itemid = eid;
							}
						}
					}
					if ( userid != null && itemid != null && writeData) {
						ratings_writer.append(userid);
						ratings_writer.append(",");
						ratings_writer.append(itemid);
						ratings_writer.append(",");
						ratings_writer.append(Double.toString(ratingscore));
						ratings_writer.append("\n");
					}
				} else if(rtype.equals(eof)) {
					return false;
				}
				
				return true;

	}
	
	
}
