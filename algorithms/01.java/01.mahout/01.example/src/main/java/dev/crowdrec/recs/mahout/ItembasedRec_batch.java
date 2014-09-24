package dev.crowdrec.recs.mahout;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.StringReader;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.util.List;

import javax.json.Json;
import javax.json.JsonObject;
import javax.json.JsonReader;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;

import org.zeromq.ZMQ;
import org.zeromq.ZMQ.Socket;
import org.zeromq.ZMQ.Context;
import org.zeromq.ZMsg;
import org.zeromq.ZFrame;

public class ItembasedRec_batch {

	private static final String OUTMSG_READY = "READY";
	private static final String OUTMSG_OK = "OK";
	private static final String OUTMSG_KO = "KO";

	private static final String RECOMMEND_CMD = "RECOMMEND";
	private static final String TRAIN_CMD = "TRAIN";
	private static final String READINPUT_CMD = "READ_INPUT";
	private static final String STOP_CMD = "STOP";

	private static final String TMP_MAHOUT_USERRATINGS_FILENAME = "mahout_ratings.csv";
	private static final boolean INPUT_FILE_HAS_HEADER = true;

	private String stagedir = null;
	private Socket communication_socket = null;

	/**
	 *
	 * @param args
	 * $0: stage directory: directory where the algorithm can persist data (e.g., temp files, models,..)
	 * $1: communication directory: directory reserved to communication messages
	 * @throws IOException
	 * @throws NumberFormatException
	 * @throws TasteException
	 */
	public static void main(String[] args) throws NumberFormatException, IOException, TasteException {

		if ( args.length < 2 ) {
			System.out.println("missing parameters");
			return;
		}

		String outdir = args[0];
		String comm = args[1];

		System.out.println("ALGO: ZMQ creating context");
		Context context = ZMQ.context(1);
		System.out.println("ALGO: ZMQ created context");
		System.out.println("ALGO: ZMQ creating socket");
		Socket comm_sock = context.socket(ZMQ.REQ);
		System.out.println("ALGO: ZMQ created context");
		comm_sock.setReceiveTimeOut(10000);
		System.out.println("ALGO: ZMQ setting timeout");
		System.out.println("ALGO: ZMQ connecting to socket");
		comm_sock.connect(comm);
		System.out.println("ALGO: ZMQ connected to socket");

		ItembasedRec_batch ubr = new ItembasedRec_batch(outdir, comm_sock);
		ubr.run();

		comm_sock.close();
		context.term();
	}

	public ItembasedRec_batch(String stagedir, Socket socket) throws IOException {
		this.stagedir = stagedir;
		this.communication_socket = socket;

		System.out.println("ALGO: machine started");
	}

	public void run() throws IOException, TasteException {
		Recommender recommender = null;
		boolean stop = false;

		System.out.println("ALGO: sending READY message");
		communication_socket.send(OUTMSG_READY, 0);
		while ( !stop ) {
			ZMsg recvMsg = null;
			while ( recvMsg == null ) {
				recvMsg = ZMsg.recvMsg(this.communication_socket);
			}
			System.out.println("ALGO: received message: " + recvMsg.toString());
			ZFrame command = recvMsg.remove();

			if (command.streq(READINPUT_CMD)) {
				System.out.println("ALGO: running READ INPUT cmd");
				boolean success = cmdReadinput(recvMsg);

				System.out.println(success ? "ALGO: input correctly read" : "ALGO: failing input read");
				communication_socket.send(success ? OUTMSG_OK : OUTMSG_KO);
			} else if (command.streq(TRAIN_CMD)) {
				System.out.println("ALGO: running TRAIN cmd");
				try {
					recommender = createRecommender(stagedir + File.separator + TMP_MAHOUT_USERRATINGS_FILENAME);

					System.out.println("ALGO: recommender created");
					communication_socket.send(OUTMSG_OK);
				} catch (TasteException e) {
					communication_socket.send(OUTMSG_KO);
				}
			} else if (command.streq(RECOMMEND_CMD)) {
				System.out.println("ALGO: running RECOMMEND cmd");
				ZMsg recomms = null;
				boolean success = (recommender != null && (recomms = cmdRecommend(recvMsg, recommender)).size() > 0 ) ;

				System.out.println(success ? "ALGO: recommedation completed correctly" : "ALGO: failure in generating recommendations");
				if (success)
					recomms.addFirst(OUTMSG_OK);
				else
					recomms.addFirst(OUTMSG_KO);

				recomms.send(communication_socket);
			} else if (command.streq(STOP_CMD)) {
				communication_socket.send(OUTMSG_OK);
				stop = true;
			} else {
				System.out.println("ALGO: unknown command");
			}

		}
		System.out.println("shutdown");
	}

	/*
		subject_etype    user
		subject_eid    1001
		request_timestamp    1404910899
		request_properties    {"device":["smartphone", "android"], "location":"home"}
		recomm_properties    { "explanation":"suggested by your close friends"}
		linked_entities    [{"id":"movie:2001","rating":3.8,"rank":3}, {"id":"movie:2002","rating":4.3,"rank":1}, {"id":"movie:2003","rating":4,"rank":2,"explanation":{"reason":"you like","entity":"movie:2004"}}]
	*/
	protected ZMsg cmdRecommend(ZMsg msg, Recommender recommender) throws IOException, TasteException {
		int reclen = Integer.parseInt( msg.remove().toString() );

		ZMsg recomms = new ZMsg();
		for (ZFrame entityIdStr : msg) {
			String[] entityEls = entityIdStr.toString().split(":");
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
				} else {
					// do nothing
				}
				sb.append("]");
				recomms.addString(sb.toString());
			} else {
				// TODO: manage error
			}
		}

		return recomms;
	}

	protected boolean cmdReadinput(ZMsg msg) throws IOException {
		if (msg.size() != 2) {
			// wrong number of elements
			return false;
		}

		String entities_filename = msg.remove().toString();
		String relations_filename = msg.remove().toString();
		if ( entities_filename != null && relations_filename != null ) {
			convertDataset(stagedir, entities_filename, relations_filename, "user","movie","rating.explicit");
			return true;
		} else {
			// TODO: manage missing data
			return false;
		}
	}

	protected Recommender createRecommender(String filename) throws IOException, TasteException{
		DataModel model = new FileDataModel(new File(filename));
		ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
		Recommender recommender = new GenericItemBasedRecommender(model, similarity);
		return recommender;
	}

	protected void convertDataset(String outdir, String entities_filename, String relations_filename, String user_etype, String movie_etype, String rating_rtype) throws NumberFormatException, IOException {
		BufferedReader relations_reader = null;
		BufferedWriter ratings_writer = null;
		try {
			File ratings_file = new File(outdir + File.separator + TMP_MAHOUT_USERRATINGS_FILENAME);
			if ( ratings_file.exists() ) {
				ratings_file.delete();
			}
			ratings_writer = new BufferedWriter(new FileWriter(ratings_file));
			relations_reader = new BufferedReader(new FileReader(relations_filename));
			String line = (INPUT_FILE_HAS_HEADER) ? relations_reader.readLine() : null; // skip first line (if true)
			while ( (line = relations_reader.readLine()) != null ) {
				String[] els = line.split("\t");
				String rtype = els[0];

				if ( rtype.equals(rating_rtype) ) {
					String rid = els[1];
					long ts = Long.parseLong( els[2] );
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
					if ( userid != null && itemid != null ) {
						ratings_writer.append(userid);
						ratings_writer.append(",");
						ratings_writer.append(itemid);
						ratings_writer.append(",");
						ratings_writer.append(Double.toString(ratingscore));
						ratings_writer.append("\n");
					}
				}
			}
		} finally {
			if ( relations_reader != null ) {
				relations_reader.close();
			}
			if ( ratings_writer != null ) {
				ratings_writer.close();
			}
		}

	}
}
