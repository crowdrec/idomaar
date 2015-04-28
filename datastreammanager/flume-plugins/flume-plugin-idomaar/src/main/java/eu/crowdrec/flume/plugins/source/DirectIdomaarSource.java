/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package eu.crowdrec.flume.plugins.source;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.zip.GZIPInputStream;

import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.EventDrivenSource;
import org.apache.flume.conf.Configurable;
import org.apache.flume.event.EventBuilder;
import org.apache.flume.lifecycle.LifecycleState;
import org.apache.flume.source.AbstractSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;

public class DirectIdomaarSource extends AbstractSource implements EventDrivenSource, Configurable {

	private static final Logger logger = LoggerFactory.getLogger(DirectIdomaarSource.class);
	
	private static final List<String> FORMATS = Lists.newArrayList("plain", "gzip");

	private String fileName;
	private Charset charset;
	private String format;
	private int batchSize = 100;

	private BufferedReader reader;
	
	private volatile boolean endSent;
	
	private class EventCreator implements Runnable {

		@Override
		public void run() {
			endSent = false;
			Map<String, String> header = Maps.newHashMap();
			while (getLifecycleState() == LifecycleState.START) {
				List<String> batch = Lists.newArrayList(); 
				String line;
				while ((line = getNextLine()) != null && batch.size() < batchSize) batch.add(line);
				List<Event> eventBatch = Lists.newArrayList();
				for (String inputLine: batch) {
					Event event = EventBuilder.withBody(inputLine, charset, header);
					eventBatch.add(event);
					Map<String, String> headers = Maps.newHashMap();
					String randomString = UUID.randomUUID().toString(); 
					headers.put("key", randomString);
					event.setHeaders(headers);
				}
				if (batch.size() < batchSize && !endSent) {
					logger.info("Sending <END>");
					Event event = EventBuilder.withBody("<END>", charset, header);
					eventBatch.add(event);
					endSent = true;
				}
				getChannelProcessor().processEventBatch(eventBatch);
				if (batch.size() < batchSize) stop();
			}
		}
		
		private String getNextLine() {
			try {
				return reader.readLine();
			} catch (IOException exception) {
				throw new RuntimeException(exception);
			}
		}
	}

	@Override
	public void configure(Context context) {
		fileName = context.getString("fileName", null);
		charset = Charset.forName(context.getString("charset", "UTF-8"));
		format = context.getString("format", null);
		if (fileName == null) throw new RuntimeException("File name is not configured for " + getClass().getSimpleName());
		if (format == null || !FORMATS.contains(format)) throw new RuntimeException("Format not specified or unknown " + format);
	}
	
	@Override
	public void start() {
		logger.info("Starting source with file name {}", fileName);
		super.start();
		try {
			File inputFile = new File(fileName);
			if (format.equals("plain")) {
				reader = Files.newBufferedReader(inputFile.toPath(), charset);
			} else if (format.equals("gzip")) {
				InputStream fileStream = new FileInputStream(inputFile);
				InputStream gzipStream = new GZIPInputStream(fileStream);
				Reader decoder = new InputStreamReader(gzipStream, "UTF-8");
				reader = new BufferedReader(decoder);
			}
		} catch (IOException exception) {
			throw new RuntimeException();
		}
		new Thread(new EventCreator()).start();
	}
	
	@Override
	public void stop() {
		logger.info("Stopping ...");
		try {
			reader.close();
		} catch (IOException exception) {
			logger.error("Unable to close reader.", exception);
		}
		super.stop();
	}
}