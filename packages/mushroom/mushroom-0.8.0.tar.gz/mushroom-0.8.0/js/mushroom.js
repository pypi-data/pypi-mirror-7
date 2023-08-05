/**
 * @author Michael P. Jung
 * @preserve mushroom.js
 * Copyright (C) 2012-2013 Michael P. Jung
 */

(function(undefined) {

/**
 * Check if value is undefined and return the defaultValue in this case.
 * @param value {*} value to check if it is undefined
 * @param defaultValue {*} fallback value if `value` is undefined
 * @returns {*} value if value is not undefined or the default value
 */
function defaultIfUndefined(value, defaultValue) {
	return value !== undefined ? value : defaultValue;
}

// create empty mushroom namespace
var mushroom = window.mushroom;
if (mushroom === undefined) {
	mushroom = window.mushroom = {};
}

/**
 * Base class for all exceptions.
 * @constructor
 */
mushroom.Exception = function(message) {
	this.message = message;
};

mushroom.Exception.prototype = new Error();
mushroom.Exception.prototype.name = 'mushroom.Exception';

/**
 * This exception is thrown when trying to call an operation on an
 * object which is currently in the wrong state.
 * @extends mushroom.Exception
 * @constructor
 */
mushroom.IllegalState = function(message) {
	this.message = message;
};

mushroom.IllegalState.prototype = new mushroom.Exception();
mushroom.IllegalState.prototype.name = 'mushroom.IllegalState';

/**
 * This exception is sent when an error occurs while trying to
 * connect to the server. e.g. Server not responding, timeout,
 * non 200 status codes, etc.
 * @extends mushroom.Exception
 * @constructor
 */
mushroom.ConnectionError = function(message) {
	this.message = message;
};

mushroom.ConnectionError.prototype = new mushroom.Exception();
mushroom.ConnectionError.prototype.name = 'mushroom.ConnectionError';

/**
 * This exception is sent when an error response is received for
 * which no error handler is registered.
 * @param request {Object} request object as sent from the client
 * @param response {Object} error response object as received from
 *                          the server
 * @extends mushroom.Exception
 * @constructor
 */
mushroom.RequestFailed = function(request, response) {
	this.message = 'Method call failed: ' + request.method;
	this.request = request;
	this.response = response;
};

mushroom.RequestFailed.prototype = new mushroom.Exception();
mushroom.RequestFailed.prototype.name = 'mushroom.RequestFailed';

/**
 * Signal class which allows distribution of signals. This class is
 * used by the mushroom Client class to notify the user code about
 * various state changes.
 * @constructor
 */
mushroom.Signal = function Signal() {
	this.handlers = [];
};

/**
 * Send event to all connected handlers.
 * This function takes any number of arguments which are
 * passed 1:1 to the connected handler functions.
 */
mushroom.Signal.prototype.send = function() {
	var args = arguments;
	this.handlers.forEach(function(handler) {
		handler.apply(this, args);
	}.bind(this));
};

/**
 * Connect a handler to the signal. The handler will be called with
 * the same arguments that are given to the Signal.send() function.
 * @param handler {Function} handler the handler to be connected
 */
mushroom.Signal.prototype.connect = function(handler) {
	this.handlers.push(handler);
};

/**
 * Disconnect handler from the signal. After disconnecting the handler
 * it will no longer receive events from the signal. Calling disconnect
 * on a handler that is not connected is silently ignored.
 * @param {Function} handler the handler to be disconnected
 */
mushroom.Signal.prototype.disconnect = function(handler) {
	var index = this.handlers.indexOf(handler);
	if (index !== -1) {
		this.handlers.splice(index, 1);
	}
};

/**
 * Disconnect all handlers.
 */
mushroom.Signal.prototype.disconnectAll = function() {
	this.handlers.splice(0);
};

function createXHR() {
	try {
		return new window.XMLHttpRequest();
	} catch(e) {}
	try {
		return new window.ActiveXObject('Microsoft.XMLHTTP');
	} catch(e) {}
}

/**
 * This field defines whether WebSocket support is available or not.
 * @define
 */
var WEB_SOCKET_SUPPORT = 'WebSocket' in window;

function post(url, data, callback, errorCallback) {
	var xhr = createXHR();
	xhr.open('POST', url, true);
	xhr.onreadystatechange = function() {
		if (xhr.readyState === 4) {
			if (xhr.status == 200) {
				callback(xhr);
			} else {
				errorCallback(xhr);
			}
		}
	};
	/* In order to make so called 'simple requests' that work via CORS
	 * the Content-Type is very limited. We simply use text/plain which
	 * is better than using form-data content types.
	 * https://developer.mozilla.org/en/http_access_control#Simple_requests
	 */
	if (data !== null) {
		xhr.setRequestHeader('Content-Type', 'text/plain');
		xhr.send(JSON.stringify(data));
	} else {
		xhr.send(null);
	}
}


/**
 * The mushroom client class.
 * @param {Object} options
 * @constructor
 */
mushroom.Client = function(options) {
	this.url = options.url;
	this.transports = options.transports ||
			(WEB_SOCKET_SUPPORT ? ['ws', 'poll'] : ['poll']);
	this.transport = null;
	this.methods = options.methods || {};
	this.queue = new mushroom.MessageQueue();
	this.requests = {};

	this.signals = {
		// This signal is sent when a request returns an error and
		// no errorCallback was specified.
		error: new mushroom.Signal(),
		// This signal is sent when the connection is established.
		connected: new mushroom.Signal(),
		// This signal is sent when the connection was terminated.
		disconnected: new mushroom.Signal()
	};

	// FIXME this requires jQuery
	/*
	$(window).bind('beforeunload', function() {
		// FIXME It seems that this call should be done asynchronously
		//       which might not work for cross domain requests at all.
		//       We need to find a good solution here or use a shorter
		//       timeout value in order to detect disconnects earlier at
		//       the server side.
		this.disconnect();
	}.bind(this));
	*/
};

/**
 * Start connecting to remote server. This function is asynchronous and
 * upon connection success the `connected` signal is sent.
 * @returns {undefined}
 */
mushroom.Client.prototype.connect = function(auth) {
	var request = {
		transports: this.transports,
		auth: auth || null
	};
	post(this.url, request, function(xhr) {
		var jsonResponse = JSON.parse(xhr.responseText);
		var transportClass = mushroom.transports[jsonResponse.transport];
		if (transportClass === undefined) {
			this.signals.error.send(new mushroom.ConnectionError(
					'Unsupported transport ' + this.transport));
			return;
		}
		this.transport = new transportClass(this, jsonResponse);
		this.transport.start();
	}.bind(this), function(xhr) {
		this.signals.error.send(new mushroom.ConnectionError(
				'Transport negotiation failed. Status code=' + xhr.status));
	}.bind(this));
};

/**
 * Disconnect client from server.
 * @throws mushroom.Exception
 */
mushroom.Client.prototype.disconnect = function() {
	// FIXME check current state of transport
	this.sendMessage(new mushroom.Disconnect({
		client: this
	}));
};

/**
 * Register a client method
 * @param name {String} name of the method
 * @param callback {Function} callback function which should
 *                            handle method calls for this method name
 */
mushroom.Client.prototype.method = function(name, callback) {
	this.methods[name] = callback;
	return this;
};

/**
 * Send notification to the server.
 * @param method {String} name of the method to be called
 * @param data {*} data the request data
 */
mushroom.Client.prototype.notify = function(method, data) {
	var notification = new mushroom.Notification({
		client: this,
		method: method,
		data: data
	});
	this.queue.push(notification);
	this.sendMessage(notification);
};

/**
 * Retrieve request object from requests object while
 * removing it from there. This method is used to retrieve
 * the request object when receiving a response or error.
 */
mushroom.Client.prototype.popRequest = function(id) {
	var request = this.requests[id];
	delete this.requests[id];
	return request;
};

/**
 * Send request to the server.
 * @param method {String} name of the method to be called
 * @param data {*} data the request data
 * @param responseCallback {Function} callback which is called
 *     when the response is received.
 * @param errorCallback {Function} callback which is called
 *     when an error response is received. If no callback is
 *     provided the global error signal is used instead.
 */
mushroom.Client.prototype.request = function(method, data, responseCallback, errorCallback) {
	if (responseCallback === undefined) {
		throw Error("responseCallback is mandatory");
	}
	var request = new mushroom.Request({
		client: this,
		method: method,
		data: data,
		responseCallback: responseCallback,
		errorCallback: errorCallback
	});
	this.queue.push(request);
	this.requests[request.messageId] = request;
	this.sendMessage(request);
};

/**
 * Send message
 * @param message {Object}
 */
mushroom.Client.prototype.sendMessage = function(message) {
	if (this.transport !== null && this.transport.state == mushroom.STATE.CONNECTED) {
		this.transport.sendMessage(message);
	}
};

/**
 * Handle a notification received from the server
 * @param notification {Object}
 */
mushroom.Client.prototype.handleNotification = function(notification) {
	var method = this.methods[notification.method];
	if (method !== undefined) {
		method.call(this, notification);
	} else {
		this.signals.error(new mushroom.Exception(
				'No method for notification: ' + notification.method));
	}
};

/**
 * Handle a response received from the server
 * @param response {Object}
 */
mushroom.Client.prototype.handleResponse = function(response) {
	var request = this.popRequest(response.requestMessageId);
	request.responseCallback(response.data);
};

/**
 * Handle an error response received from the server.
 * @param error {Object}
 */
mushroom.Client.prototype.handleError = function(error) {
	var request = this.popRequest(error.requestMessageId);
	if (request.errorCallback === undefined) {
		// No errorCallback given. Send an error signal.
		this.signals.error.send(new mushroom.RequestFailed(
				request, error));
	} else {
		request.errorCallback(error.data);
	}
};

/**
 * Handle a disconnect message received from the server.
 */
mushroom.Client.prototype.handleDisconnect = function() {
	this.transport.stop();
	this.transport = null;
	this.signals.disconnected.send();
};

/**
 * Message queue class for outbound messages. This class is used to queue
 * outbound messages until they are acknowledged by the server. If the
 * connection is lost before the message has been acknowledged it will be
 * retransmitted as soon as the connection is reestablished.
 */
mushroom.MessageQueue = function() {
	this.nextMessageId = 0;
	this.messages = [];
};

/**
 * Add message to the queue.
 * @param message {Object} object to be added
 * @returns {Number} message id of the added message
 */
mushroom.MessageQueue.prototype.push = function(message) {
	if (message.messageId !== null) {
		throw new mushroom.Exception('Message does already have a message id');
	}
	message.messageId = this.nextMessageId;
	this.messages.push(message);
	this.nextMessageId += 1;
	return message.messageId;
};

/**
 * Acknowledge messages. This removes all messages with with a
 * messageId less or equal than the given messageId from the queue.
 * @param messageId {Number}
 */
mushroom.MessageQueue.prototype.ack = function(messageId) {
	if (messageId >= this.nextMessageId) {
		throw new mushroom.Exception('Can not acknowledge a message id that was never part of this queue');
	}
	var i;
	for (i=0; i<this.messages.length; ++i) {
		var message = this.messages[i];
		if (message.messageId > messageId) {
			// First message found which is not acknowledged.
			break;
		}
	}
	this.messages.splice(0, i);
};

/**
 * Call function for every message in the queue.
 * @param f {Function} the function to be called
 */
mushroom.MessageQueue.prototype.forEach = function(f) {
	var i;
	for (i=0; i<this.messages.length; ++i) {
		var message = this.messages[i];
		f(message);
	}
};

/**
 * Constants for the state of the client and its transport.
 * <pre>
 *        .------> [DISCONNECTED] ------.
 *        |              ^   ^          |
 *        |              |   |          |
 * [DISCONNECTING]       |   |      connect()
 *        |              |   |          |
 *        |              |   |          |
 *        |              |   |          v
 *   disconnect()        |   '---- [CONNECTING]
 *        |              |              |
 *        |              |              |
 *        '-------- [CONNECTED] <-------'
 * </pre>
 */
mushroom.STATE = {
	DISCONNECTED: 'DISCONNECTED',
	DISCONNECTING: 'DISCONNECTING',
	CONNECTING: 'CONNECTING',
	CONNECTED: 'CONNECTED'
};

/**
 * Transport for the HTTP poll protocol.
 * @param client {mushroom.Client} The client object which is notified
 *     about inbound messages and state changes of the transport
 * @param options {Object}
 */
mushroom.PollTransport = function(client, options) {
	this.client = client;
	this.url = options.url;
	this.lastMessageId = null;
	this.state = mushroom.STATE.DISCONNECTED;
};

/**
 * Start the poll transport. This causes the transport to send poll
 * requests until either the client or the server sides decides to
 * disconnect or a timeout happens.
 */
mushroom.PollTransport.prototype.start = function() {
	if (this.state != mushroom.STATE.DISCONNECTED) {
		throw new mushroom.IllegalState('Already started');
	}
	this.poll();
};

/**
 * Stop the poll transport.
 */
mushroom.PollTransport.prototype.stop = function() {
	if (this.state == mushroom.STATE.DISCONNECTED) {
		throw new mushroom.IllegalState('Already stopped');
	}
	this.state = mushroom.STATE.DISCONNECTING;
};

/**
 * Perform a poll request.
 */
mushroom.PollTransport.prototype.poll = function() {
	this.state = mushroom.STATE.CONNECTED;
	this.client.signals.connected.send();
	// XXX This is the same for all transports - move this logic
	//     into the client.
	this.client.queue.forEach(this.sendMessage.bind(this));
	var request = [
		[0, this.lastMessageId]
	];
	post(this.url, request, function(xhr) {
		var data = JSON.parse(xhr.responseText);
		data.forEach(function(messageData) {
			var message = mushroom.messageFromData(messageData, this.client);
			if ('messageId' in message) {
				if (message.messageId <= this.lastMessageId &&
						this.lastMessageId !== null) {
					// skip messages which we have already processed
					return;
				}
				this.lastMessageId = message.messageId;
			}
			var messageName = message.constructor.MESSAGE_NAME;
			var handler = this.client['handle' + messageName];
			handler.call(this.client, message);
		}.bind(this));
		if (this.state == mushroom.STATE.DISCONNECTING) {
			this.state = mushroom.STATE.DISCONNECTED;
			this.client.signals.disconnected.send();
		} else {
			this.poll();
		}
	}.bind(this), function() {
		this.state = mushroom.STATE_DISCONNECTED;
		// FIXME calling handleDisconnect is probably wrong as this method
		// is reserved for handling "Disconnect" messages received from the
		// server.
		this.client.handleDisconnect();
	}.bind(this));
};

/**
 * Send message to the server.
 */
mushroom.PollTransport.prototype.sendMessage = function(message) {
	// FIXME
	// Add a browser timeout so it is possible to send two or more
	// messages at the same time. Also make sure to check if there
	// is already a send request running.
	var request = [
		message.toList()
	];
	post(this.url, request, function() {
		// FIXME remove message from out-queue
	}.bind(this), function() {
		// FIXME log error
	}.bind(this));
};

/**
 * The WebSocket transport.
 * @param client {mushroom.Client} The client object which is notified
 *     about inbound messages and state changes of the transport
 * @param options {Object}
 * @constructor
 */
mushroom.WebSocketTransport = function(client, options) {
	this.client = client;
	this.url = options.url;
	this.state = mushroom.STATE.DISCONNECTED;
};

/**
 * Start the WebSocket transport. This causes the WebSocket transport
 * to connect to the server and stay connected.
 */
mushroom.WebSocketTransport.prototype.start = function() {
	this.ws = new WebSocket(this.url);
	this.ws.onopen = function() {
		this.state = mushroom.STATE.CONNECTED;
		this.client.signals.connected.send();
		// XXX This is the same for all transports - move this logic
		//     into the client.
		this.client.queue.forEach(this.sendMessage.bind(this));
	}.bind(this);
	this.ws.onclose = function() {
		this.state = mushroom.STATE.DISCONNECTED;
		this.client.handleDisconnect();
	}.bind(this);
	this.ws.onmessage = function(event) {
		var messageData = JSON.parse(event.data);
		var message = mushroom.messageFromData(messageData, this.client);
		if ('messageId' in message) {
			if (message.messageId <= this.lastMessageId &&
					this.lastMessageId !== null) {
				// skip messages which we have already processed
				return;
			}
			this.lastMessageId = message.messageId;
		}
		var messageName = message.constructor.MESSAGE_NAME;
		var handler = this.client['handle' + messageName];
		handler.call(this.client, message);
	}.bind(this);
};

/**
 * Stop the WebSocket transport.
 */
mushroom.WebSocketTransport.prototype.stop = function() {
	if (this.ws !== null) {
		this.ws.close();
		this.ws = null;
	}
};

/**
 * Send message to the server.
 * @param message {Object}
 */
mushroom.WebSocketTransport.prototype.sendMessage = function(message) {
	var data = message.toList();
	var frame = JSON.stringify(data);
	this.ws.send(frame);
};

mushroom.transports = {
	'poll': mushroom.PollTransport,
	'ws': mushroom.WebSocketTransport
};

/**
 * Interface that has to be implemented by the different message types.
 * @interface
 */
mushroom.Message = function() {};
mushroom.Message.prototype.toList = function() {};

/**
 * @param {*} options
 * @constructor
 * @implements {mushroom.Message}
 */
mushroom.Heartbeat = function(options) {
	this.client = options.client;
	this.lastMessageId = options.lastMessageId;
};

/** @const */
mushroom.Heartbeat.MESSAGE_CODE = 0;

/** @const */
mushroom.Heartbeat.MESSAGE_NAME = 'Heartbeat';

/** @override */
mushroom.Heartbeat.prototype.toList = function() {
	return [mushroom.Heartbeat.MESSAGE_CODE, this.lastMessageId];
};

/**
 * @param {*} options
 * @constructor
 * @implements {mushroom.Message}
 */
mushroom.Notification = function(options) {
	this.client = options.client;
	this.messageId = defaultIfUndefined(options.messageId, null);
	this.method = options.method;
	this.data = options.data;
};

/** @const */
mushroom.Notification.MESSAGE_CODE = 1;

/** @const */
mushroom.Notification.MESSAGE_NAME = 'Notification';

/** @override */
mushroom.Notification.prototype.toList = function() {
	return [mushroom.Notification.MESSAGE_CODE, this.messageId,
			this.method, this.data];
};

/**
 * @param {*} options
 * @constructor
 * @implements {mushroom.Message}
 */
mushroom.Request = function(options) {
	this.client = options.client;
	this.messageId = defaultIfUndefined(options.messageId, null);
	this.method = options.method;
	this.data = options.data || null;
	this.responseCallback = options.responseCallback;
	this.errorCallback = options.errorCallback;
};

/** @const */
mushroom.Request.MESSAGE_CODE = 2;

/** @const */
mushroom.Request.MESSAGE_NAME = 'Request';

/** @override */
mushroom.Request.prototype.toList = function() {
	return [mushroom.Request.MESSAGE_CODE, this.messageId,
			this.method, this.data];
};

mushroom.Request.prototype.sendResponse = function(data) {
	var response = new mushroom.Response({
		client: this.client,
		requestMessageId: this.messageId,
		data: data
	});
	this.client.queue.push(response);
	this.client.sendMessage(response);
};

mushroom.Request.prototype.sendError = function(data) {
	var error = new mushroom.Error({
		client: this.client,
		requestMessageId: this.messageId,
		data: data
	});
	this.client.queue.push(error);
	this.client.sendMessage(error);
};

/**
 * @param {*} options
 * @constructor
 * @implements {mushroom.Message}
 */
mushroom.Response = function(options) {
	this.client = options.client;
	this.messageId = defaultIfUndefined(options.messageId, null);
	this.requestMessageId = options.requestMessageId;
	this.data = options.data || null;
};

/** @const */
mushroom.Response.MESSAGE_CODE = 3;

/** @const */
mushroom.Response.MESSAGE_NAME = 'Response';

mushroom.Response.prototype.success = true;

/**
 * @param {*} options
 * @constructor
 * @implements {mushroom.Message}
 */
mushroom.Error = function(options) {
	this.client = options.client;
	this.messageId = defaultIfUndefined(options.messageId, null);
	this.requestMessageId = options.requestMessageId;
	this.data = options.data || null;
};

/** @const */
mushroom.Error.MESSAGE_CODE = 4;

/** @const */
mushroom.Error.MESSAGE_NAME = 'Error';

mushroom.Error.prototype.success = false;

/** @override */
mushroom.Error.prototype.toList = function() {
	return [mushroom.Error.MESSAGE_CODE, this.messageId,
			this.requestMessageId, this.data];
};

/**
 * @param {*} options
 * @constructor
 * @implements {mushroom.Message}
 */
mushroom.Disconnect = function(options) {
	this.client = options.client;
};

/** @const */
mushroom.Disconnect.MESSAGE_CODE = -1;

/** @const */
mushroom.Disconnect.MESSAGE_NAME = 'Disconnect';

/** @override */
mushroom.Disconnect.prototype.toList = function() {
	return [mushroom.Disconnect.MESSAGE_CODE];
};

/**
 *
 * @param data
 * @param {mushroom.Client} client
 *
 * @returns {mushroom.Message}
 */
mushroom.messageFromData = function(data, client) {
	switch (data[0]) {
		case mushroom.Heartbeat.MESSAGE_CODE:
			return new mushroom.Heartbeat({
				client: client,
				lastMessageId: data[1]
			});
		case mushroom.Notification.MESSAGE_CODE:
			return new mushroom.Notification({
				client: client,
				messageId: data[1],
				method: data[2],
				data: data[3]
			});
		case mushroom.Request.MESSAGE_CODE:
			return new mushroom.Request({
				client: client,
				messageId: data[1],
				method: data[2],
				data: data[3]
			});
		case mushroom.Response.MESSAGE_CODE:
			return new mushroom.Response({
				client: client,
				messageId: data[1],
				requestMessageId: data[2],
				data: data[3]
			});
		case mushroom.Error.MESSAGE_CODE:
			return new mushroom.Error({
				client: client,
				messageId: data[1],
				requestMessageId: data[2],
				data: data[3]
			});
		case mushroom.Disconnect.MESSAGE_CODE:
			return new mushroom.Disconnect({
				client: client
			});
		default:
			throw new mushroom.Exception(
					'Unsupported message code: ' + data[0]);
	}
};

})();
