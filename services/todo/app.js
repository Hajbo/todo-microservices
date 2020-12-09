var express = require("express");
var app = express();
var bodyParser = require("body-parser");
var { initTracer, tracingMiddleWare} = require("./tracing");
const router = express.Router();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

// RabbitMQ consumer
var amqp = require('amqplib/callback_api');
const queue_name = "todo_user_delete";
const TodoItem = require("./models/todoItemModel");

function consumer(conn) {
  var ok = conn.createChannel(on_open);
  function on_open(err, ch) {
    if (err != null) bail(err);
    ch.assertQueue(queue_name);
    ch.consume(queue_name, function(msg) {
      if (msg !== null) {
        console.log("Deleting: " + msg.content.toString());
        var jsonData = JSON.parse(msg.content);
        console.log(jsonData.uuid);
        TodoItem.deleteMany({"uuid": jsonData.uuid}, function(err, result) {
          if (err) {
            console.log("ERROR while deleting " + jsonData.uuid + ": " + err);
          } else {
            console.log("Deleted TODOS for uuid " + jsonData.uuid);
          }
        });
        ch.ack(msg);
      }
    });
  }
}

amqp.connect('amqp://rabbit', function(err, conn) {
    if (err != null) console.log("ERROR: " + err + "\nRetrying until Rabbit is up.");
    consumer(conn);
  });

// Init tracer
const tracer = initTracer('todo-service')
const opentracing = require('opentracing')
opentracing.initGlobalTracer(tracer)
// Instrument every incomming request
app.use(tracingMiddleWare)


const getActualRequestDurationInMilliseconds = start => {
    const NS_PER_SEC = 1e9; // convert to nanoseconds
    const NS_TO_MS = 1e6; // convert to milliseconds
    const diff = process.hrtime(start);
    return (diff[0] * NS_PER_SEC + diff[1]) / NS_TO_MS;
  };
let demoLogger = (req, res, next) => {
let current_datetime = new Date();
let formatted_date =
    current_datetime.getFullYear() +
    "-" +
    (current_datetime.getMonth() + 1) +
    "-" +
    current_datetime.getDate() +
    " " +
    current_datetime.getHours() +
    ":" +
    current_datetime.getMinutes() +
    ":" +
    current_datetime.getSeconds();
let method = req.method;
let url = req.url;
let status = res.statusCode;
const start = process.hrtime();
const durationInMilliseconds = getActualRequestDurationInMilliseconds(start);
let log = `[${formatted_date}] ${method}:${url} ${status} ${durationInMilliseconds.toLocaleString()} ms`;
console.log(log);
next();
};
app.use(demoLogger);


app.use("/todos", require("./routes/todoRoutes"));


app.listen(8080);
console.log("Listening to PORT 8080");
