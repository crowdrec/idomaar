package eu.crowdrec.recs.mahout;

import java.io.IOException;
import java.io.StringReader;
import java.util.List;

import javax.json.Json;
import javax.json.JsonObject;
import javax.json.JsonReader;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.zeromq.ZMsg;
import org.zeromq.ZMQ.Socket;

public class RecommendationEngine implements Runnable {
	Socket responder;
	Recommender recom;
	
	private boolean shutdown = false;
	
	public RecommendationEngine(Socket socket_response, Recommender recommender) {
		responder = socket_response;
		recom = recommender;
		
		System.out.println("Starting engine recommender=["+recom+"]");
	}
	
	@Override
	public void run() {
		
			
		
		 while (!shutdown && !Thread.currentThread().isInterrupted()) {
	            //  Wait for next request from client

			 	ZMsg recvMsg =  ZMsg.recvMsg(responder);
	            System.out.println("Received request: ["+recvMsg+"].");
	           
				try {
					String messageType = recvMsg.remove().toString();
					
					if (messageType.equals("RECOMMEND")) {
						ZMsg msg = cmdRecommend(recvMsg);
						msg.send(responder);
					} else {
						System.out.println("Unable to parse event " + messageType);
						responder.send("KO");
					}
				} catch (IOException e) {
					shutdown = true;
					e.printStackTrace();
				} catch (TasteException e) {
					// TODO ADD MESSAGE TO RESPONSE
					e.printStackTrace();
					responder.send(e.toString());
				} catch (Exception e) {
					shutdown = true;
					e.printStackTrace();
				}
	           
	        }
		
	}


	
	public void stop() {
		this.shutdown=true;
	}
	
	/*
	subject_etype    user
	subject_eid    1001
	request_timestamp    1404910899
	request_properties    {"device":["smartphone", "android"], "location":"home"}
	recomm_properties    { "explanation":"suggested by your close friends"}
	linked_entities    [{"id":"movie:2001","rating":3.8,"rank":3}, {"id":"movie:2002","rating":4.3,"rank":1}, {"id":"movie:2003","rating":4,"rank":2,"explanation":{"reason":"you like","entity":"movie:2004"}}]
*/
protected ZMsg cmdRecommend(ZMsg msg) throws Exception {
	
	JsonReader reader = Json.createReader(new StringReader(msg.remove().toString()));
	JsonObject properties = reader.readObject();
	
	JsonReader reader_rel = Json.createReader(new StringReader(msg.remove().toString()));
	JsonObject linkedEntities = reader_rel.readObject();
	

	
	int reclen = properties.getInt("reclen");

	ZMsg recomms = new ZMsg();

	String[] entityEls = linkedEntities.getString("subject").split(":");
		if ( entityEls.length == 2 ) {
			String etype = entityEls[0];
			long eid = Long.parseLong(entityEls[1]);
			StringBuilder sb = new StringBuilder();
			sb.append(etype).append("\t");
			sb.append(Long.toString(eid)).append("\t");
			sb.append(System.currentTimeMillis()).append("\t");
			sb.append("{}").append("\t");
			sb.append("{\"reclen\":").append(Integer.toString(reclen)).append("}").append("\t");
			sb.append("[");
			List<RecommendedItem> reclist = recom.recommend(eid, reclen);
			if ( reclist != null && reclist.size() > 0 ) {
				int rank = 0;
				for ( RecommendedItem item : reclist ) {
					rank++;
					if ( rank > 1 ) {
						sb.append(",");
					}
					sb.append("{");
					sb.append("\"id\":\"").append(item.getItemID()).append("\"");
					sb.append(",");
					sb.append("\"rating\":\"").append(item.getValue()).append("\"");
					sb.append(",");
					sb.append("\"rank\":\"").append(Integer.toString(rank)).append("\"");
					sb.append("}");
				}
			} else {
				// do nothing
			}
			sb.append("]");
			recomms.addString(sb.toString());
		} else {
				throw new Exception("Entity elements length <> 2, current length="+ entityEls.length);
		}
	
	return recomms;
}

}
