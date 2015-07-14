package eu.crowdrec.recs.mahout;

import java.io.StringReader;
import java.util.List;

import javax.json.Json;
import javax.json.JsonObject;
import javax.json.JsonReader;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.zeromq.ZMQ;
import org.zeromq.ZMsg;
import org.zeromq.ZMQ.Socket;

public class RecommendationEngine implements Runnable {

	private static String zeromqBindPort = "5560";

	private final Recommender recommender;

	private boolean shutdown = false;
	private final String recommendationSocketAddress;

	public RecommendationEngine(Recommender recommender) {
		this.recommender = recommender;
		System.out.println("Starting engine recommender=["+ this.recommender +"]");
		String zeromqBindAddress = "0.0.0.0";
		recommendationSocketAddress = "tcp://" + zeromqBindAddress + ":" + zeromqBindPort;
	}

	private ZMsg createResponse(ZMsg request) {
		String messageType = request.remove().toString();
		switch (messageType) {
			case "HELLO-RECOMMENDER-ENGINE":
				return ZMsg.newStringMsg("HELLO THERE");
			case "RECOMMEND":
				try {
					return cmdRecommend(request);
				} catch (TasteException e) {
					// TODO ADD MESSAGE TO RESPONSE
					e.printStackTrace();
					return ZMsg.newStringMsg(e.toString());
				} catch (Exception e) {
					shutdown = true;
					e.printStackTrace();
					return ZMsg.newStringMsg(e.toString());
				}
			default:
				System.out.println("Unable to parse event " + messageType);
				return ZMsg.newStringMsg("KO");
		}
	}

	@Override
	public void run() {
		ZMQ.Context context = ZMQ.context(1);
		Socket recommendationSocket = context.socket(ZMQ.REP);
		System.out.println("Creating recommendation ZMQ socket and binding to " + recommendationSocketAddress);
		recommendationSocket.bind(recommendationSocketAddress);
		while (!shutdown && !Thread.currentThread().isInterrupted()) {
			ZMsg recommendationRequest =  ZMsg.recvMsg(recommendationSocket);
			ZMsg response = createResponse(recommendationRequest);
			try {
				response.send(recommendationSocket);
			}
			catch (Exception exception) {
				System.out.println("Exception occurred while sending response: " + exception.getMessage());
				exception.printStackTrace();
			}
		}
	}


	/*
	timestamp    1404910899
	recomm_properties    { "explanation":"suggested by your close friends"}
	linked_entities    [{"id":"movie:2001","rating":3.8,"rank":3}, {"id":"movie:2002","rating":4.3,"rank":1}, {"id":"movie:2003","rating":4,"rank":2,"explanation":{"reason":"you like","entity":"movie:2004"}}]
*/
	protected ZMsg cmdRecommend(ZMsg msg) throws Exception {

		String jsonString = msg.remove().toString();

		JsonReader reader = Json.createReader(new StringReader(jsonString));
		JsonObject properties = reader.readObject();

		JsonReader reader_rel = Json.createReader(new StringReader(msg.remove().toString()));
		JsonObject linkedEntities = reader_rel.readObject();

		int reclen = properties.getInt("reclen");

		System.err.println("Received recommendation request properties=[" + properties.toString() + "] linkedEntities=["+ linkedEntities.toString() +"]");


		ZMsg recomms = new ZMsg();

		String[] entityEls = linkedEntities.getString("subject").split(":");
		if ( entityEls.length == 2 ) {
			String etype = entityEls[0];
			long eid = Long.parseLong(entityEls[1]);
			StringBuilder sb = new StringBuilder();
			sb.append("{}").append("\t");
			sb.append("[");
			List<RecommendedItem> reclist = recommender.recommend(eid, reclen);
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
			}
			sb.append("]");

			System.err.println("New recommendation result [" + sb +"]");
			recomms.addString(sb.toString());
		} else {
			throw new Exception("Entity elements length <> 2, current length="+ entityEls.length);
		}

		return recomms;
	}

	public String getAddress(String ipAddressToThisHost) {
		return "tcp://" + ipAddressToThisHost + ":" + zeromqBindPort;
	}
}
