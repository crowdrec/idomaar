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
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.util.List;
import java.util.Map;

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

	private String fileName;
	private Charset charset;
	private int batchSize = 100;

	private BufferedReader reader;
	
	private class EventCreator implements Runnable {

		@Override
		public void run() {
			Map<String, String> header = Maps.newHashMap();
			while (getLifecycleState() == LifecycleState.START) {
				List<String> batch = Lists.newArrayList(); 
				String line;
				while ((line = getNextLine()) != null && batch.size() < batchSize) batch.add(line);
				List<Event> eventBatch = Lists.newArrayList();
				for (String inputLine: batch) eventBatch.add(EventBuilder.withBody(inputLine, charset, header));
				if (batch.size() < batchSize) eventBatch.add(EventBuilder.withBody("<END>", charset, header));
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
		if (fileName == null) throw new RuntimeException("File name is not configured for " + getClass().getSimpleName());
	}
	
	@Override
	public void start() {
		logger.info("Starting source with file name {}", fileName);
		super.start();
		try {
			reader = Files.newBufferedReader(new File(fileName).toPath(), charset);
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